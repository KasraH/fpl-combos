# VPS Deployment Guide

## Quick Setup (Recommended)

### 1. Copy files to your VPS

```bash
# On your local machine
scp -r webapp/ user@your-vps-ip:/home/user/fpl-webapp/

# OR clone from git if you've pushed to a repository
ssh user@your-vps-ip
git clone <your-repo-url> fpl-webapp
cd fpl-webapp/webapp
```

### 2. Deploy with Docker Compose

```bash
# On your VPS
cd /home/user/fpl-webapp
docker-compose up -d --build
```

### 3. Set up Nginx (if not already configured)

```bash
# Copy nginx config
sudo cp nginx.conf.example /etc/nginx/sites-available/fpl-webapp
sudo ln -s /etc/nginx/sites-available/fpl-webapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Alternative: Manual Setup

### 1. Install Python and dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx
```

### 2. Set up the application

```bash
cd /home/user
git clone <your-repo> fpl-webapp
cd fpl-webapp/webapp

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create systemd service

```bash
sudo nano /etc/systemd/system/fpl-webapp.service
```

Add this content:

```ini
[Unit]
Description=FPL Player Combination Web App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/fpl-webapp/webapp
Environment=PATH=/home/user/fpl-webapp/webapp/venv/bin
Environment=FLASK_ENV=production
Environment=PORT=5000
ExecStart=/home/user/fpl-webapp/webapp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable fpl-webapp
sudo systemctl start fpl-webapp
sudo systemctl status fpl-webapp
```

## Configuration Options

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Port to run on (default: 5000)
- `HOST`: Host to bind to (default: 0.0.0.0)

### Nginx Configuration

- Update `your-domain.com` in nginx.conf.example with your actual domain/IP
- If you don't have SSL, comment out SSL-related lines
- Adjust SSL certificate paths if needed

## Monitoring

### Check logs

```bash
# Docker logs
docker-compose logs -f fpl-webapp

# Systemd logs
sudo journalctl -u fpl-webapp -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health check

```bash
curl http://localhost:5000/
```

## Maintenance

### Update the app

```bash
# Pull latest changes
git pull

# Docker method
docker-compose down
docker-compose up -d --build

# Manual method
sudo systemctl restart fpl-webapp
```

### Backup cache

```bash
# The cache is stored in ./fpl_cache/
tar -czf fpl-cache-backup-$(date +%Y%m%d).tar.gz fpl_cache/
```

## Firewall

Make sure your VPS firewall allows the port:

```bash
# UFW example
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000  # Only if accessing directly, not needed with nginx

# Check status
sudo ufw status
```

## Access

- **With Nginx**: http://your-domain-or-ip/
- **Direct access**: http://your-domain-or-ip:5000/

## Troubleshooting

1. **App not starting**: Check logs with `docker-compose logs` or `journalctl`
2. **Can't connect**: Verify firewall and nginx configuration
3. **Cache issues**: Ensure `fpl_cache/` directory has proper permissions
4. **Memory issues**: Monitor with `docker stats` or `htop`
