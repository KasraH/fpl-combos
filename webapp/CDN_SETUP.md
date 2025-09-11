# CDN Deployment Setup

## After choosing "CDN (automated setup)" on Namespace:

### 1. Namespace will provide you with:

- A CDN URL/endpoint
- Instructions to point your DNS to their CDN

### 2. DNS Configuration:

Instead of pointing directly to your VPS, you'll point to Namespace CDN:

- A record: `yourdomain.me` → `cdn-endpoint-provided-by-namespace`
- CNAME record: `www.yourdomain.me` → `yourdomain.me`

### 3. VPS Configuration:

Your VPS will receive traffic from the CDN (not directly from users):

- SSL is handled by CDN (automatic)
- Your nginx receives HTTP requests from CDN
- CDN forwards HTTPS requests to your VPS as HTTP

### 4. Benefits:

- ✅ Automatic SSL certificate management
- ✅ Global CDN performance boost
- ✅ DDoS protection from CDN
- ✅ Reduced server load
- ✅ Better caching for static assets

### 5. Updated nginx config:

The nginx-fpl.conf has been updated to work with CDN:

- Removed SSL configuration (handled by CDN)
- Added proper forwarded headers
- Configured for HTTP backend with HTTPS frontend

### 6. Deployment process remains the same:

1. Choose CDN setup on Namespace
2. Deploy to VPS using deploy.sh
3. Update DNS to point to CDN (not directly to VPS)
4. Test via your domain

This setup is actually better than direct SSL because you get CDN benefits too!
