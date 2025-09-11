#!/bin/bash

# FPL Webapp Deployment Script for VPS

set -e  # Exit on any error

echo "🚀 Deploying FPL Webapp to VPS..."

# Configuration
APP_NAME="fpl-webapp"
REPO_URL="https://github.com/yourusername/fpl_player_combination.git"  # Update this
DOMAIN="yourdomain.me"  # Update this
APP_DIR="/home/$(whoami)/apps/fpl-webapp"
NGINX_CONFIG="/etc/nginx/sites-available/fpl-webapp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root"
    exit 1
fi

# Create app directory
print_status "Creating application directory..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    print_status "Updating existing repository..."
    git pull origin master
else
    print_status "Cloning repository..."
    git clone "$REPO_URL" .
fi

# Build and start Docker containers
print_status "Building and starting Docker containers..."
cd webapp
docker-compose down --remove-orphans || true
docker-compose build --no-cache
docker-compose up -d

# Wait for container to be ready
print_status "Waiting for container to start..."
sleep 10

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    print_status "Container started successfully!"
else
    print_error "Container failed to start. Check logs:"
    docker-compose logs
    exit 1
fi

# Setup Nginx (requires sudo)
print_status "Setting up Nginx reverse proxy..."
echo "You'll need to run these commands manually with sudo:"
echo ""
echo "sudo cp nginx-fpl.conf $NGINX_CONFIG"
echo "sudo ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/"
echo "sudo nginx -t"
echo "sudo systemctl reload nginx"
echo ""

# Setup SSL certificate (manual step)
print_warning "SSL Certificate Setup:"
echo "1. Download your SSL certificate files from Namespace"
echo "2. Upload them to your VPS:"
echo "   - Certificate file: /etc/ssl/certs/$DOMAIN.crt"
echo "   - Private key file: /etc/ssl/private/$DOMAIN.key"
echo "3. Update the nginx configuration with correct paths"
echo ""

# Display status
print_status "Deployment completed!"
echo ""
echo "📊 Container Status:"
docker-compose ps
echo ""
echo "📋 Next Steps:"
echo "1. Configure SSL certificates"
echo "2. Setup Nginx reverse proxy (commands shown above)"
echo "3. Update DNS to point $DOMAIN to this server"
echo "4. Test the application at http://localhost:5001"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs: docker-compose logs -f"
echo "  Restart app: docker-compose restart"
echo "  Stop app: docker-compose down"
echo "  Update app: ./deploy.sh"