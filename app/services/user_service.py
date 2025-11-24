"""
Service layer for User and Employee management.
Handles CRUD operations for combined User-Employee entities.
"""
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User, UserRole
from app.models.employee import Employee
from app.schemas.user_management import UserEmployeeCreate, UserEmployeeUpdate, UserEmployeeResponse
from app.core.security import get_password_hash


def create_user_and_employee(db: Session, data: UserEmployeeCreate) -> User:
    """
    Create a new User and their associated Employee profile in a single transaction.
    
    Args:
        db: Database session
        data: UserEmployeeCreate schema with user and employee fields
        
    Returns:
        Created User object with employee relationship loaded
        
    Raises:
        HTTPException: If email already exists, invalid role, or manager_id doesn't exist
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{data.email}' already exists"
        )
    
    # Validate role
    try:
        role_enum = UserRole[data.role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: '{data.role}'. Must be one of: {', '.join([r.value for r in UserRole])}"
        )
    
    # Validate manager_id if provided
    if data.manager_id is not None:
        manager = db.query(Employee).filter(Employee.id == data.manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manager with employee ID {data.manager_id} not found"
            )
    
    # Create User
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=role_enum,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.flush()  # Get user.id without committing
    
    # Create Employee
    employee = Employee(
        user_id=user.id,
        department=data.department,
        job_title=data.job_title,
        manager_id=data.manager_id
    )
    db.add(employee)
    
    # Commit transaction
    db.commit()
    db.refresh(user, ["employee"])
    
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID with their employee profile.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object with employee relationship loaded, or None if not found
    """
    return db.query(User).options(
        joinedload(User.employee)
    ).filter(User.id == user_id).first()


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    department: Optional[str] = None
):
    """Get all users with optional filtering and pagination.

    Filtering rules (case-insensitive partial matches):
    - name: matches against User.full_name
    - email: matches against User.email
    - department: matches Employee.department (requires join)

    Args:
        db: Database session
        skip: Pagination offset
        limit: Pagination limit (capped at 100)
        name: Optional case-insensitive substring of full_name
        email: Optional case-insensitive substring of email
        department: Optional case-insensitive substring of department

    Returns:
        List[User] with employee relationship loaded
    """
    if limit > 100:
        limit = 100

    query = db.query(User).options(joinedload(User.employee))

    # Apply filters
    if name:
        query = query.filter(User.full_name.ilike(f"%{name}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if department:
        # Join Employee only if department filter specified to avoid unnecessary join overhead
        query = query.join(Employee).filter(Employee.department.ilike(f"%{department}%"))

    return query.offset(skip).limit(limit).all()


def update_user_and_employee(db: Session, user_id: int, data: UserEmployeeUpdate) -> Optional[User]:
    """
    Update a User and/or their Employee profile with partial updates.
    
    Args:
        db: Database session
        user_id: User ID to update
        data: UserEmployeeUpdate schema with optional fields
        
    Returns:
        Updated User object, or None if not found
        
    Raises:
        HTTPException: If email already exists, invalid role, or manager_id doesn't exist
    """
    # Get user with employee
    user = db.query(User).options(
        joinedload(User.employee)
    ).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # Extract user and employee update data
    update_dict = data.model_dump(exclude_unset=True)
    
    # Separate user and employee fields
    user_fields = {"email", "password", "full_name", "role", "is_active"}
    employee_fields = {"department", "job_title", "manager_id"}
    
    user_updates = {k: v for k, v in update_dict.items() if k in user_fields}
    employee_updates = {k: v for k, v in update_dict.items() if k in employee_fields}
    
    # Update User fields
    if user_updates:
        # Check email uniqueness if email is being updated
        if "email" in user_updates and user_updates["email"] != user.email:
            existing_user = db.query(User).filter(User.email == user_updates["email"]).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{user_updates['email']}' already exists"
                )
        
        # Validate and convert role if provided
        if "role" in user_updates:
            try:
                user_updates["role"] = UserRole[user_updates["role"].upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role: '{user_updates['role']}'. Must be one of: {', '.join([r.value for r in UserRole])}"
                )
        
        # Hash password if provided
        if "password" in user_updates:
            user_updates["hashed_password"] = get_password_hash(user_updates.pop("password"))
        
        # Apply user updates
        for field, value in user_updates.items():
            setattr(user, field, value)
    
    # Update Employee fields
    if employee_updates:
        # Validate manager_id if being updated
        if "manager_id" in employee_updates and employee_updates["manager_id"] is not None:
            manager = db.query(Employee).filter(Employee.id == employee_updates["manager_id"]).first()
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Manager with employee ID {employee_updates['manager_id']} not found"
                )
        
        # Check if employee exists, create if not
        if not user.employee:
            employee = Employee(
                user_id=user.id,
                department=employee_updates.get("department"),
                job_title=employee_updates.get("job_title"),
                manager_id=employee_updates.get("manager_id")
            )
            db.add(employee)
        else:
            # Apply employee updates
            for field, value in employee_updates.items():
                setattr(user.employee, field, value)
    
    # Commit transaction
    db.commit()
    db.refresh(user, ["employee"])
    
    return user


def delete_user_and_employee(db: Session, user_id: int) -> bool:
    """
    Delete a User and their associated Employee profile.
    
    Note: Since the foreign key user_id in employees table doesn't have CASCADE configured,
    we need to manually delete the Employee record first.
    
    Args:
        db: Database session
        user_id: User ID to delete
        
    Returns:
        True if deleted successfully
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Delete Employee first (if exists) due to foreign key constraint
    if user.employee:
        db.delete(user.employee)
    
    # Delete User
    db.delete(user)
    
    # Commit transaction
    db.commit()
    
    return True
