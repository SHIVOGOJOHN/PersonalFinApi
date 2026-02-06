# Backend Deployment Guide

## Quick Start for Render Deployment

### 1. Prepare Your Repository

Make sure your backend folder has these files:
- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `.env.example` - Template for environment variables
- `.gitignore` - Excludes .env from git
- `README.md` - This file

### 2. Push to GitHub

```bash
# From the Android directory
git init
git add .
git commit -m "Initial commit - Personal Finance Manager"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3. Deploy on Render

1. Go to [https://dashboard.render.com/](https://dashboard.render.com/)
2. Sign up or log in
3. Click **New +** → **Web Service**
4. Click **Connect a repository** → Select your GitHub repo
5. Configure the service:

   **Basic Settings**:
   - Name: `finance-manager-api` (or your choice)
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Region: Choose closest to you
   - Branch: `main`

   **Build & Deploy**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. Click **Advanced** and add Environment Variables:

   ```
   DB_HOST=your-mysql-host.com
   DB_PORT=19274
   DB_USER=your-username
   DB_PASSWORD=your-secure-password
   DB_NAME=defaultdb
   DB_CHARSET=utf8mb4
   DB_CONNECTION_TIMEOUT=10
   ```
   
   **Note**: Use your actual MySQL credentials from the `.env` file.

7. Click **Create Web Service**

### 4. Wait for Deployment

- First deployment takes 2-5 minutes
- Watch the logs for any errors
- Once you see "Application startup complete", it's ready!

### 5. Get Your API URL

After deployment, you'll see a URL like:
```
https://finance-manager-api.onrender.com
```

### 6. Test Your API

Open in browser:
```
https://your-app-name.onrender.com/
```

You should see:
```json
{
  "message": "Personal Finance Manager API",
  "version": "1.0.0",
  "status": "running"
}
```

Test health endpoint:
```
https://your-app-name.onrender.com/health
```

### 7. Update Mobile App

Edit `config.py` in the main Android directory:

```python
# Change this line:
API_BASE_URL = "http://localhost:8000"

# To your Render URL:
API_BASE_URL = "https://your-app-name.onrender.com"
```

Then rebuild your APK if needed.

## Important Notes

### Free Tier Limitations

Render free tier:
- ✅ 750 hours/month (enough for one app)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold start takes 30-60 seconds

**Solution**: First request after inactivity will be slow, subsequent requests are fast.

### Security

- ✅ Environment variables are encrypted on Render
- ✅ HTTPS enabled by default
- ✅ No credentials in code
- ⚠️ Consider adding API authentication for production

### Monitoring

- View logs in Render dashboard
- Check health endpoint: `/health`
- Monitor database connections

## Troubleshooting

### Build Failed

**Error**: `ModuleNotFoundError`
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility

**Error**: `Database connection failed`
- Verify environment variables are set correctly
- Check MySQL server is accessible from Render

### App Not Starting

**Check logs** in Render dashboard:
- Look for Python errors
- Verify port binding (must use `$PORT`)
- Check database connection

### Database Issues

**Connection timeout**:
- Increase `DB_CONNECTION_TIMEOUT` to 30
- Check MySQL server status
- Verify firewall allows Render IPs

## Alternative Deployment Options

### Railway
1. Connect GitHub repo
2. Add environment variables
3. Deploy automatically

### Heroku
```bash
heroku create finance-api
heroku config:set DB_HOST=your-host
# ... set other env vars
git push heroku main
```

### DigitalOcean App Platform
1. Create new app
2. Connect repository
3. Add environment variables
4. Deploy

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run server
python main.py

# Or with auto-reload
uvicorn main:app --reload
```

## API Endpoints

- `GET /` - API info
- `POST /backup` - Backup data
- `GET /restore` - Restore data
- `GET /health` - Health check

See [main.py](main.py) for detailed endpoint documentation.
