# Railway Deployment Guide for Astral Aggregator

This guide provides step-by-step instructions for deploying your FastAPI-based website change detection system on Railway.

## Why Railway?

Railway is the **recommended platform** for your Astral Aggregator because:

✅ **Perfect for FastAPI apps** - Native Python support  
✅ **Built-in PostgreSQL** - Managed database included  
✅ **Background processing** - Great for scheduled change detection tasks  
✅ **Easy environment management** - Simple secrets and variables  
✅ **Automatic deployments** - Git-based deployment workflow  
✅ **Good pricing** - $5/month starter plan with generous limits  

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Firecrawl API Key**: You'll need a valid Firecrawl API key
3. **Railway Account**: Sign up at [railway.app](https://railway.app)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains these files:
- `Dockerfile` ✅ (already created)
- `requirements.txt` ✅ (already created)
- `railway.json` ✅ (already created)
- `.dockerignore` ✅ (already created)

### 2. Deploy to Railway

#### Option A: Deploy via Railway Dashboard

1. **Sign up/Login**: Go to [railway.app](https://railway.app) and sign in
2. **Create Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select Repository**: Choose your Astral Aggregator repository
4. **Auto-Deploy**: Railway will automatically detect the Dockerfile and start building
5. **Wait for Build**: The build process takes 2-5 minutes

#### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Configure Environment Variables

In your Railway project dashboard:

1. Go to your project → "Variables" tab
2. Add these environment variables:

```bash
# Required
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Optional (Railway provides these automatically)
DATABASE_URL=postgresql://...  # Railway auto-provides
PORT=8000                      # Railway auto-provides
RAILWAY_STATIC_URL=your-app-url # Railway auto-provides

# Optional custom variables
LOG_LEVEL=INFO
PYTHONPATH=/app
```

### 4. Add PostgreSQL Database (Optional)

If you need persistent storage:

1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically provide the `DATABASE_URL` environment variable
3. Your app will automatically connect to the database

### 5. Configure Custom Domain (Optional)

1. Go to your service → "Settings" → "Domains"
2. Add your custom domain
3. Railway will provide SSL certificates automatically

## Testing Your Deployment

### 1. Health Check
Visit your Railway app URL (e.g., `https://astral-aggregator-production.up.railway.app`) to see:
```json
{
  "status": "healthy",
  "service": "astral-api",
  "version": "0.0.1",
  "message": "Welcome to the Astral API - Website Change Detection System"
}
```

### 2. API Documentation
Visit `/docs` for interactive FastAPI documentation:
- `https://your-app.railway.app/docs`

### 3. Test Endpoints
```bash
# Check system status
curl https://your-app.railway.app/api/listeners/status

# Trigger change detection
curl -X POST https://your-app.railway.app/api/listeners/trigger/judiciary_uk

# View changes
curl https://your-app.railway.app/api/listeners/changes/judiciary_uk
```

## Railway-Specific Features

### Automatic Deployments
- Every push to your main branch triggers a new deployment
- Railway builds and deploys automatically
- No manual intervention needed

### Environment Management
- Separate environments for development, staging, and production
- Easy variable management through the dashboard
- Secure secrets storage

### Monitoring & Logs
- Real-time logs in the Railway dashboard
- Built-in monitoring and health checks
- Automatic restarts on failures

### Scaling
- Easy scaling through the dashboard
- Multiple replicas for high availability
- Automatic load balancing

## Troubleshooting

### Common Issues

#### 1. Build Failures
**Problem**: Docker build fails
**Solution**: 
- Check the build logs in Railway dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify the Dockerfile syntax

#### 2. Environment Variables
**Problem**: App can't find required variables
**Solution**:
- Double-check all variables are set in Railway dashboard
- Ensure variable names match exactly (case-sensitive)
- Restart the service after adding variables

#### 3. Port Issues
**Problem**: App not accessible
**Solution**:
- Railway automatically provides the `PORT` environment variable
- Ensure your app listens on `0.0.0.0:$PORT`
- Check the service logs for port binding errors

#### 4. Database Connection
**Problem**: Can't connect to PostgreSQL
**Solution**:
- Verify `DATABASE_URL` is set correctly
- Check if the database service is running
- Ensure your app handles database connection gracefully

### Debugging Commands

```bash
# View logs
railway logs

# Check service status
railway status

# Restart service
railway service restart

# Open shell in container
railway shell
```

## Cost Optimization

### Railway Pricing
- **Starter Plan**: $5/month (recommended for your use case)
- **Pro Plan**: $20/month (for higher traffic)
- **Enterprise**: Custom pricing

### Cost-Saving Tips
1. **Use Starter Plan**: Perfect for development and moderate usage
2. **Optimize Builds**: The provided Dockerfile is optimized for faster builds
3. **Monitor Usage**: Check Railway dashboard for resource usage
4. **Scale Down**: Reduce replicas during low-traffic periods

## Production Considerations

### Security
- All environment variables are encrypted
- Automatic SSL certificates
- Secure database connections
- No need to manage secrets manually

### Performance
- Global CDN included
- Automatic load balancing
- Built-in caching layers
- Optimized container images

### Backup & Recovery
- Automatic database backups (if using Railway PostgreSQL)
- Easy rollback to previous deployments
- Git-based version control

## Next Steps

1. **Monitor**: Set up alerts for your app's health
2. **Scale**: Add more replicas if needed
3. **Custom Domain**: Add your own domain name
4. **Database**: Set up PostgreSQL for persistent storage
5. **CI/CD**: Configure automatic testing before deployment

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Community**: [discord.gg/railway](https://discord.gg/railway)
- **Status**: [status.railway.app](https://status.railway.app)

Your Astral Aggregator is now ready for production use on Railway! 🚀 