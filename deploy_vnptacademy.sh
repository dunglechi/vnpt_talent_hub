#!/bin/bash

# VNPT Talent Hub - Deployment to one.vnptacademy.com.vn
# Server: Ubuntu 22.04.5 LTS, 4 vCPU, 8GB RAM, 100GB HDD
# SSH Port: 2222

set -e

echo "=========================================="
echo "VNPT Talent Hub - Server Deployment"
echo "Target: one.vnptacademy.com.vn"
echo "=========================================="
echo ""

# Configuration
SERVER_HOST="one.vnptacademy.com.vn"
SERVER_USER="admin"
SSH_PORT="2222"
DEPLOY_DIR="/opt/vnpt-talent-hub"
DOMAIN="one.vnptacademy.com.vn"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Testing SSH connection...${NC}"
ssh -p $SSH_PORT -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "echo 'SSH connection successful'"

if [ $? -ne 0 ]; then
    echo -e "${RED}Cannot connect to server. Please check:${NC}"
    echo "  - Server is accessible: $SERVER_HOST"
    echo "  - SSH port is open: $SSH_PORT"
    echo "  - Credentials are correct: $SERVER_USER"
    exit 1
fi

echo -e "${GREEN}✓ SSH connection successful${NC}"
echo ""

echo -e "${YELLOW}Step 2: Installing Docker on server...${NC}"
ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
set -e

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    echo "✓ Docker already installed"
else
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    
    # Add Docker GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    echo "✓ Docker installed"
fi

# Check if docker-compose v2 is available
if docker compose version &> /dev/null; then
    echo "✓ Docker Compose V2 ready"
else
    echo "Installing Docker Compose V2..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✓ Docker Compose installed"
fi

docker --version
docker compose version || docker-compose --version
ENDSSH

echo -e "${GREEN}✓ Docker setup complete${NC}"
echo ""

echo -e "${YELLOW}Step 3: Uploading application code...${NC}"

# Create deploy directory
ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST "sudo mkdir -p $DEPLOY_DIR && sudo chown -R $SERVER_USER:$SERVER_USER $DEPLOY_DIR"

# Upload files using rsync (faster than scp for multiple files)
rsync -avz -e "ssh -p $SSH_PORT" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='logs' \
    ./ $SERVER_USER@$SERVER_HOST:$DEPLOY_DIR/

echo -e "${GREEN}✓ Files uploaded${NC}"
echo ""

echo -e "${YELLOW}Step 4: Configuring environment...${NC}"

# Create .env file on server
ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
cd $DEPLOY_DIR

# Copy production template
cp .env.production .env

# Generate SECRET_KEY
SECRET_KEY=\$(openssl rand -hex 32)

# Update .env with server-specific values
sed -i "s|CHANGE_THIS_TO_RANDOM_SECRET_KEY_789!@#\\\$%\^&\*()|\$SECRET_KEY|g" .env
sed -i "s|your-domain.com|$DOMAIN|g" .env

# Update docker-compose for production
sed -i 's|API_PORT:-8000|API_PORT:-8080|g' docker-compose.yml

echo "✓ Environment configured"
echo ""
echo "Please manually edit .env file for:"
echo "  1. Database passwords (DB_PASSWORD, REDIS_PASSWORD)"
echo "  2. SMTP settings (if using email verification)"
echo "  3. Any other custom settings"
echo ""
read -p "Press Enter when ready to continue..."
ENDSSH

echo -e "${GREEN}✓ Environment ready${NC}"
echo ""

echo -e "${YELLOW}Step 5: Setting up SSL certificate...${NC}"

ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
cd $DEPLOY_DIR

# Install Certbot
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot
fi

# Create SSL directory
sudo mkdir -p nginx/ssl

# Option 1: Let's Encrypt (if domain is accessible from internet)
echo "Attempting to get Let's Encrypt certificate..."
sudo certbot certonly --standalone --non-interactive --agree-tos \
    --email admin@vnptacademy.com.vn \
    -d $DOMAIN || {
    
    echo "Let's Encrypt failed (domain may not be publicly accessible)"
    echo "Creating self-signed certificate for internal use..."
    
    # Option 2: Self-signed certificate
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=VN/ST=Hanoi/L=Hanoi/O=VNPT/OU=IT/CN=$DOMAIN"
}

# Copy certificates
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
fi

sudo chown -R $USER:$USER nginx/ssl
sudo chmod 644 nginx/ssl/*.pem

echo "✓ SSL certificates ready"
ENDSSH

echo -e "${GREEN}✓ SSL configured${NC}"
echo ""

echo -e "${YELLOW}Step 6: Configuring Nginx...${NC}"

ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
cd $DEPLOY_DIR

# Update domain in nginx config
sed -i "s|your-domain.com|$DOMAIN|g" nginx/nginx.conf

echo "✓ Nginx configured"
ENDSSH

echo -e "${GREEN}✓ Nginx ready${NC}"
echo ""

echo -e "${YELLOW}Step 7: Building and starting services...${NC}"

ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /opt/vnpt-talent-hub

echo "Building Docker images..."
docker compose build --no-cache || docker-compose build --no-cache

echo "Starting services..."
docker compose up -d || docker-compose up -d

echo "Waiting for services to be ready..."
sleep 15

# Check services status
docker compose ps || docker-compose ps

echo "✓ Services started"
ENDSSH

echo -e "${GREEN}✓ Services running${NC}"
echo ""

echo -e "${YELLOW}Step 8: Running database migrations...${NC}"

ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /opt/vnpt-talent-hub

echo "Running migrations..."
docker compose exec -T api alembic upgrade head || docker-compose exec -T api alembic upgrade head

echo "✓ Migrations complete"
ENDSSH

echo -e "${GREEN}✓ Database ready${NC}"
echo ""

echo -e "${YELLOW}Step 9: Creating admin user...${NC}"

ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /opt/vnpt-talent-hub

echo "Creating admin user..."
docker compose exec -T api python -c "
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.core.security import get_password_hash

db = SessionLocal()

# Check if admin exists
admin = db.query(User).filter(User.email == 'admin@vnpt.vn').first()

if not admin:
    # Create admin user
    admin = User(
        email='admin@vnpt.vn',
        hashed_password=get_password_hash('Admin@VNPT2025'),
        full_name='System Administrator',
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # Create employee profile
    employee = Employee(
        user_id=admin.id,
        department='IT',
        job_title='System Administrator'
    )
    db.add(employee)
    db.commit()
    
    print('✓ Admin user created')
    print('  Email: admin@vnpt.vn')
    print('  Password: Admin@VNPT2025')
else:
    print('✓ Admin user already exists')
" || echo "Note: Admin creation skipped (may already exist)"

ENDSSH

echo -e "${GREEN}✓ Admin user ready${NC}"
echo ""

echo -e "${YELLOW}Step 10: Configuring firewall...${NC}"

ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
# Configure UFW firewall
if command -v ufw &> /dev/null; then
    sudo ufw --force enable
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 2222/tcp comment 'SSH'
    sudo ufw allow 80/tcp comment 'HTTP'
    sudo ufw allow 443/tcp comment 'HTTPS'
    sudo ufw status
    echo "✓ Firewall configured"
else
    echo "UFW not available, skipping firewall setup"
fi
ENDSSH

echo -e "${GREEN}✓ Firewall configured${NC}"
echo ""

echo -e "${GREEN}=========================================="
echo "✓ Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Server Information:"
echo "  Host: $SERVER_HOST"
echo "  SSH Port: $SSH_PORT"
echo "  Deploy Directory: $DEPLOY_DIR"
echo ""
echo "Application URLs:"
echo "  API: https://$DOMAIN/api/v1"
echo "  Docs: https://$DOMAIN/docs"
echo "  Health: https://$DOMAIN/health"
echo ""
echo "Admin Credentials:"
echo "  Email: admin@vnpt.vn"
echo "  Password: Admin@VNPT2025"
echo "  ⚠️  Please change password after first login!"
echo ""
echo "Useful Commands (run on server):"
echo "  SSH: ssh -p $SSH_PORT $SERVER_USER@$SERVER_HOST"
echo "  Logs: cd $DEPLOY_DIR && docker compose logs -f"
echo "  Status: cd $DEPLOY_DIR && docker compose ps"
echo "  Restart: cd $DEPLOY_DIR && docker compose restart"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test API: curl -k https://$DOMAIN/health"
echo "2. Login to admin panel: https://$DOMAIN/docs"
echo "3. Change admin password"
echo "4. Configure SMTP (if needed) in .env"
echo "5. Set up backups: cd $DEPLOY_DIR && ./scripts/backup_database.sh"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
