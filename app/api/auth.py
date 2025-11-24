"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Optional
import secrets

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    generate_refresh_token_string
)
from app.models.user import User, UserRole
from app.models.email_verification_token import EmailVerificationToken
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditAction
from app.core.rate_limit import login_rate_limiter, verify_request_rate_limiter
from app.services.email_service import get_email_service
from app.services.audit_service import log_login_success, log_login_failure, log_logout, log_token_refresh, get_client_ip
from app.schemas.auth import (
    Token,
    UserResponse,
    UserCreate,
    UserUpdate
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

VERIFICATION_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register new user
    
    - **email**: Unique email address
    - **password**: Strong password (min 8 characters)
    - **full_name**: User's full name
    - **role**: User role (user/admin/manager)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    from app.core.security import get_password_hash
    db_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role or "user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token, dependencies=[Depends(login_rate_limiter())])
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login with refresh token rotation
    
    - **username**: Email address
    - **password**: User password
    
    Returns access token for authentication and sets refresh token in HttpOnly cookie
    """
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt
        log_login_failure(db=db, email=form_data.username, request=request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Generate and store refresh token
    refresh_token_string = generate_refresh_token_string()
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_string,
        expires_at=refresh_token_expires
    )
    db.add(refresh_token)
    db.commit()
    
    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token_string,
        httponly=True,
        secure=True,  # Only send over HTTPS in production
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Convert days to seconds
    )
    
    # Log successful login
    log_login_success(db=db, user_id=user.id, email=user.email, request=request)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/verify/request", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_request_rate_limiter())])
async def request_email_verification(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Request a new email verification token (sends email)."""
    if current_user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    # Invalidate previous unused tokens (optional cleanup)
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == current_user.id,
        EmailVerificationToken.consumed.is_(False)
    ).delete()

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(datetime.timezone.utc) + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    record = EmailVerificationToken(user_id=current_user.id, token=token, expires_at=expires_at)
    db.add(record)
    db.commit()
    db.refresh(record)

    # Send verification email
    email_service = get_email_service()
    email_sent = email_service.send_verification_email(
        to=current_user.email,
        token=token,
        user_name=current_user.full_name
    )
    
    if not email_sent:
        # Log warning but don't fail the request (email might be in console mode)
        print(f"[WARNING] Failed to send verification email to {current_user.email}")

    return {"message": "Verification token issued", "expires_at": expires_at.isoformat()}

@router.get("/verify", response_model=UserResponse)
async def verify_email(token: str = Query(..., description="Email verification token"), db: Session = Depends(get_db)):
    """Verify email using token."""
    record = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()
    if not record:
        raise HTTPException(status_code=404, detail="Invalid token")
    if record.consumed:
        raise HTTPException(status_code=400, detail="Token already used")
    if record.expires_at < datetime.now(datetime.timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    record.consumed = True
    db.commit()
    db.refresh(user)

    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current logged-in user information
    
    Requires authentication
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information
    
    - **full_name**: Update full name
    - **password**: Change password (optional)
    
    Requires authentication
    """
    # Update user info
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password is not None:
        from app.core.security import get_password_hash
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    refresh_token: Optional[str] = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint - revokes refresh token and clears cookie
    
    Requires authentication
    """
    # Revoke refresh token if present
    if refresh_token:
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.user_id == current_user.id
        ).first()
        
        if token_record and not token_record.is_revoked:
            token_record.revoke()
            db.commit()
    
    # Clear refresh token cookie
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    # Log logout event
    log_logout(db=db, user_id=current_user.id, email=current_user.email, request=request)
    
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token from HttpOnly cookie
    
    Implements token rotation: old refresh token is revoked and new one issued
    
    Returns:
        New access token and sets new refresh token in cookie
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    # Find refresh token in database
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Validate token (check expiration and revocation)
    if not token_record.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or revoked"
        )
    
    # Get user
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # TOKEN ROTATION: Revoke old refresh token
    token_record.revoke()
    db.commit()
    
    # Generate new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Generate new refresh token
    new_refresh_token_string = generate_refresh_token_string()
    new_refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    new_refresh_token = RefreshToken(
        user_id=user.id,
        token=new_refresh_token_string,
        expires_at=new_refresh_token_expires
    )
    db.add(new_refresh_token)
    db.commit()
    
    # Set new refresh token in HttpOnly cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=new_refresh_token_string,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    # Log token refresh event
    log_token_refresh(db=db, user_id=user.id, email=user.email, request=request)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_current_active_manager(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to verify current user has manager role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if user is a manager
        
    Raises:
        HTTPException 403: If user does not have manager privileges
    """
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: User does not have manager privileges"
        )
    return current_user


def get_current_active_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to verify current user has admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if user is an admin
        
    Raises:
        HTTPException 403: If user does not have admin privileges
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: User does not have admin privileges"
        )
    return current_user
