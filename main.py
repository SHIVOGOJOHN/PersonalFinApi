"""
FastAPI Backend for Personal Finance Manager
Handles cloud backup and restore operations with MySQL
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
from mysql.connector import Error
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Finance Manager API",
    description="Cloud backup and restore API for Personal Finance Manager",
    version="1.0.0"
)

# Configure CORS for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL Connection Configuration from environment variables
DB_CONFIG = {
    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
    "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", "10")),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER")
}


# Pydantic Models
class Transaction(BaseModel):
    id: str
    date: str
    category: str
    type: str
    amount: float
    description: Optional[str] = ""
    created_at: str
    updated_at: str
    synced: int = 1


class Budget(BaseModel):
    id: str
    category: str
    monthly_limit: float
    created_at: str
    updated_at: str


class Category(BaseModel):
    id: str
    name: str
    type: str
    created_at: str
    icon: Optional[str] = None


class BackupData(BaseModel):
    transactions: List[Transaction]
    budgets: List[Budget]
    categories: List[Category]


class RestoreResponse(BaseModel):
    transactions: List[Dict[str, Any]]
    budgets: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]


# Database Functions
def get_db_connection():
    """Create and return MySQL database connection"""
    try:
        # Validate required environment variables
        required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("Successfully connected to MySQL database")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def init_database():
    """Initialize database tables if they don't exist"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id VARCHAR(36) PRIMARY KEY,
                date VARCHAR(10) NOT NULL,
                category VARCHAR(100) NOT NULL,
                type VARCHAR(10) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                description TEXT,
                created_at VARCHAR(20) NOT NULL,
                updated_at VARCHAR(20) NOT NULL,
                synced INT DEFAULT 1,
                INDEX idx_date (date),
                INDEX idx_type (type),
                INDEX idx_category (category)
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id VARCHAR(36) PRIMARY KEY,
                category VARCHAR(100) NOT NULL UNIQUE,
                monthly_limit DECIMAL(10, 2) NOT NULL,
                created_at VARCHAR(20) NOT NULL,
                updated_at VARCHAR(20) NOT NULL
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                type VARCHAR(10) NOT NULL,
                icon VARCHAR(50),
                created_at VARCHAR(20) NOT NULL
            )
        ''')
        
        connection.commit()
        logger.info("Database tables initialized successfully")
        
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    finally:
        cursor.close()
        connection.close()


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Personal Finance Manager API...")
    init_database()
    logger.info("API ready to accept requests")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Personal Finance Manager API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "backup": "/backup (POST)",
            "restore": "/restore (GET)",
            "health": "/health (GET)"
        }
    }


@app.post("/backup")
async def backup(data: BackupData):
    """
    Backup data to MySQL database
    Accepts transactions, budgets, and categories
    Uses REPLACE INTO for upsert behavior
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Backup transactions
        for trans in data.transactions:
            cursor.execute('''
                REPLACE INTO transactions 
                (id, date, category, type, amount, description, created_at, updated_at, synced)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                trans.id, trans.date, trans.category, trans.type,
                trans.amount, trans.description, trans.created_at,
                trans.updated_at, trans.synced
            ))
        
        # Backup budgets
        for budget in data.budgets:
            cursor.execute('''
                REPLACE INTO budgets 
                (id, category, monthly_limit, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                budget.id, budget.category, budget.monthly_limit,
                budget.created_at, budget.updated_at
            ))
        
        # Backup categories
        for cat in data.categories:
            cursor.execute('''
                INSERT INTO categories 
                (id, name, type, icon, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                icon = VALUES(icon)
            ''', (
                cat.id, cat.name, cat.type, cat.icon, cat.created_at
            ))
        
        connection.commit()
        
        logger.info(f"Backup successful: {len(data.transactions)} transactions, "
                   f"{len(data.budgets)} budgets, {len(data.categories)} categories")
        
        return {
            "status": "success",
            "message": "Backup completed successfully",
            "transactions_backed_up": len(data.transactions),
            "budgets_backed_up": len(data.budgets),
            "categories_backed_up": len(data.categories)
        }
        
    except Error as e:
        connection.rollback()
        logger.error(f"Backup error: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.get("/restore", response_model=RestoreResponse)
async def restore():
    """
    Restore all data from MySQL database
    Returns transactions, budgets, and categories
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Fetch transactions
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        transactions = cursor.fetchall()
        
        # Fetch budgets
        cursor.execute("SELECT * FROM budgets")
        budgets = cursor.fetchall()
        
        # Fetch categories
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        
        logger.info(f"Restore successful: {len(transactions)} transactions, "
                   f"{len(budgets)} budgets, {len(categories)} categories")
        
        return {
            "transactions": transactions,
            "budgets": budgets,
            "categories": categories
        }
        
    except Error as e:
        logger.error(f"Restore error: {e}")
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        connection = get_db_connection()
        connection.close()
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API is running and database is accessible"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    # Get host and port from environment or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
