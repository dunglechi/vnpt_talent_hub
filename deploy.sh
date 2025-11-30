#!/bin/bash

# VNPT Talent Hub - Production Deployment Script
# Run this script on your production server

set -e  # Exit on error

echo "======================================"
echo "VNPT Talent Hub - Production Setup"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Installing dependencies...${NC}"
apt-get update
apt-get install -y \
    docker.io \
    docker-compose \
    git \
    curl \
    certbot \
    python3-certbot-nginx

# Start Docker service
systemctl start docker
systemctl enable docker

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 2: Cloning repository...${NC}"
read -p "Enter your deployment directory [/opt/vnpt-talent-hub]: " DEPLOY_DIR
DEPLOY_DIR=${DEPLOY_DIR:-/opt/vnpt-talent-hub}

if [ -d "$DEPLOY_DIR" ]; then
    echo -e "${YELLOW}Directory exists. Pulling latest changes...${NC}"
    cd $DEPLOY_DIR
    git pull origin main
else
    git clone https://github.com/dunglechi/vnpt_talent_hub.git $DEPLOY_DIR
    cd $DEPLOY_DIR
fi

echo -e "${GREEN}✓ Repository ready${NC}"
echo ""

echo -e "${YELLOW}Step 3: Configuring environment...${NC}"
if [ ! -f .env ]; then
    cp .env.production .env
    echo -e "${YELLOW}Created .env file. Please edit it with your credentials:${NC}"
    echo "  nano .env"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Generate SECRET_KEY if not set
if grep -q "CHANGE_THIS_TO_RANDOM_SECRET_KEY" .env; then
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/CHANGE_THIS_TO_RANDOM_SECRET_KEY_789!@#\$%\^&\*()/$(echo $SECRET_KEY | sed 's/[\/&]/\\&/g')/g" .env
    echo -e "${GREEN}✓ Generated SECRET_KEY${NC}"
fi

echo ""

echo -e "${YELLOW}Step 4: Setting up SSL certificate...${NC}"
read -p "Enter your domain name: " DOMAIN_NAME
read -p "Enter your email for SSL certificate: " SSL_EMAIL

if [ ! -z "$DOMAIN_NAME" ]; then
    # Update domain in nginx config
    sed -i "s/your-domain.com/$DOMAIN_NAME/g" nginx/nginx.conf
    
    # Create SSL directory
    mkdir -p nginx/ssl
    
    # Get Let's Encrypt certificate
    echo -e "${YELLOW}Obtaining SSL certificate from Let's Encrypt...${NC}"
    certbot certonly --standalone -d $DOMAIN_NAME -d www.$DOMAIN_NAME \
        --email $SSL_EMAIL --agree-tos --non-interactive
    
    # Copy certificates
    cp /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem nginx/ssl/
    cp /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem nginx/ssl/
    
    # Set up certificate renewal
    echo "0 0,12 * * * root certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN_NAME/*.pem $DEPLOY_DIR/nginx/ssl/ && docker-compose restart nginx" >> /etc/crontab
    
    echo -e "${GREEN}✓ SSL certificate configured${NC}"
else
    echo -e "${YELLOW}⚠ Skipping SSL setup. You can configure it later.${NC}"
fi

echo ""

echo -e "${YELLOW}Step 5: Building Docker containers...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}✓ Containers built${NC}"
echo ""

echo -e "${YELLOW}Step 6: Starting services...${NC}"
docker-compose up -d

echo -e "${GREEN}✓ Services started${NC}"
echo ""

echo -e "${YELLOW}Step 7: Running database migrations...${NC}"
sleep 10  # Wait for database to be ready
docker-compose exec -T api alembic upgrade head

echo -e "${GREEN}✓ Database migrations completed${NC}"
echo ""

echo -e "${YELLOW}Step 8: Creating admin user...${NC}"
read -p "Create admin user? (y/n): " CREATE_ADMIN

if [ "$CREATE_ADMIN" = "y" ]; then
    read -p "Admin email: " ADMIN_EMAIL
    read -sp "Admin password: " ADMIN_PASSWORD
    echo ""
    
    docker-compose exec -T api python -c "
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='$ADMIN_EMAIL',
    hashed_password=get_password_hash('$ADMIN_PASSWORD'),
    full_name='System Administrator',
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)
db.add(admin)
db.commit()
print('✓ Admin user created')
"
fi

echo ""

echo -e "${YELLOW}Step 9: Setting up monitoring...${NC}"
# Create log directories
mkdir -p logs/nginx
mkdir -p logs/app
chmod -R 755 logs

echo -e "${GREEN}✓ Monitoring configured${NC}"
echo ""

echo -e "${GREEN}======================================"
echo "✓ Deployment Complete!"
echo "======================================${NC}"
echo ""
echo "Services status:"
docker-compose ps
echo ""
echo "API URL: https://$DOMAIN_NAME/api/v1"
echo "API Docs: https://$DOMAIN_NAME/docs"
echo "Health Check: https://$DOMAIN_NAME/health"
echo ""
echo -e "${YELLOW}Important next steps:${NC}"
echo "1. Verify all services are running: docker-compose ps"
echo "2. Check logs: docker-compose logs -f"
echo "3. Test API: curl https://$DOMAIN_NAME/health"
echo "4. Set up backups (see scripts/backup_database.sh)"
echo "5. Configure monitoring (see docs/DEPLOYMENT.md)"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs: docker-compose logs -f [service]"
echo "  Restart: docker-compose restart"
echo "  Stop: docker-compose down"
echo "  Update: git pull && docker-compose up -d --build"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
