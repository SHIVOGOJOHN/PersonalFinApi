# Personal Finance Manager - Backend API

FastAPI backend for cloud backup and restore operations with MySQL database.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:

```env
DB_HOST=your-mysql-host.com
DB_PORT=19274
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=defaultdb
DB_CHARSET=utf8mb4
DB_CONNECTION_TIMEOUT=10

API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Run Locally

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test API

Open browser to: `http://localhost:8000/docs`

## Deployment to Render

### 1. Push to GitHub

```bash
git add .
git commit -m "Add backend API"
git push origin main
```

### 2. Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `finance-manager-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
DB_HOST=your-mysql-host.com
DB_PORT=19274
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=defaultdb
DB_CHARSET=utf8mb4
DB_CONNECTION_TIMEOUT=10
```

### 4. Deploy

Click **Create Web Service** and wait for deployment.

### 5. Get API URL

After deployment, you'll get a URL like:
```
https://finance-manager-api.onrender.com
```

### 6. Update Mobile App

Update `config.py` in the main app:

```python
API_BASE_URL = "https://finance-manager-api.onrender.com"
```

## API Endpoints

### GET /
Root endpoint with API information

### POST /backup
Backup transactions, budgets, and categories to MySQL

**Request Body**:
```json
{
  "transactions": [...],
  "budgets": [...],
  "categories": [...]
}
```

### GET /restore
Restore all data from MySQL

**Response**:
```json
{
  "transactions": [...],
  "budgets": [...],
  "categories": [...]
}
```

### GET /health
Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "API is running and database is accessible"
}
```

## Security Notes

- ✅ All sensitive credentials in environment variables
- ✅ `.env` file excluded from git
- ✅ CORS configured (update for production)
- ✅ Error handling implemented
- ⚠️ Consider adding authentication for production

## Troubleshooting

**Database connection failed**:
- Verify environment variables are set correctly
- Check MySQL server is accessible
- Verify credentials are correct

**Port already in use**:
- Change `API_PORT` in `.env`
- Or kill process using port 8000

**Module not found**:
- Ensure all dependencies installed: `pip install -r requirements.txt`
