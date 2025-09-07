#!/usr/bin/env python3
"""
Revenue Leakage Detection System - Setup Script
This script helps set up the development environment and initial configuration.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def create_directories():
    """Create necessary directories for the project."""
    directories = [
        'data/raw',
        'data/processed',
        'data/results',
        'data/reports',
        'data/tickets',
        'logs',
        'temp',
        'web/static/css',
        'web/static/js',
        'web/static/images'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_sample_env():
    """Create a sample .env file with default values."""
    env_content = """# Database Configuration
DB_TYPE=sqlite
DB_PATH=data/revenue_detector.db
# For PostgreSQL, uncomment and configure:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=revenue_detector
# DB_USER=detector_user
# DB_PASSWORD=your_password

# Application Configuration
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=true
LOG_LEVEL=INFO
HOST=127.0.0.1
PORT=5000

# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-3.5-turbo

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL_RECIPIENTS=admin@company.com

# Analysis Configuration
ANALYSIS_SCHEDULE=0 2 * * *  # Daily at 2 AM
ENABLE_REAL_TIME_MONITORING=true
DETECTION_THRESHOLDS_CRITICAL=1000
DETECTION_THRESHOLDS_HIGH=500
DETECTION_THRESHOLDS_MEDIUM=100
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created sample .env file")
    else:
        print("ℹ .env file already exists")

def create_sample_database():
    """Create a sample SQLite database with basic schema."""
    db_path = 'data/revenue_detector.db'
    
    # Ensure data directory exists
    Path('data').mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create basic tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            transaction_date DATE,
            service_type TEXT,
            usage_amount REAL,
            billed_amount REAL,
            rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_type TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            severity TEXT NOT NULL,
            revenue_impact REAL,
            description TEXT,
            detection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'open'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigation_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            assigned_to TEXT,
            detection_ids TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Created sample SQLite database")

def create_sample_data():
    """Create some sample data for testing."""
    db_path = 'data/revenue_detector.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert sample raw data
    sample_data = [
        ('CUST001', '2024-01-15', 'Voice', 150.5, 120.0, 0.8),
        ('CUST002', '2024-01-15', 'Data', 500.0, 450.0, 0.9),
        ('CUST003', '2024-01-15', 'SMS', 100.0, 0.0, 0.1),  # Missing charge
        ('CUST004', '2024-01-15', 'Voice', 200.0, 300.0, 1.5),  # Overcharge
        ('CUST005', '2024-01-15', 'Data', 1000.0, 900.0, 0.9),
    ]
    
    cursor.executemany('''
        INSERT INTO raw_data (customer_id, transaction_date, service_type, usage_amount, billed_amount, rate)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    # Insert sample detections
    sample_detections = [
        ('missing_charges', 'CUST003', 'critical', 10.0, 'SMS charges not billed'),
        ('incorrect_rates', 'CUST004', 'high', 100.0, 'Voice rate higher than expected'),
    ]
    
    cursor.executemany('''
        INSERT INTO audit_detections (detection_type, customer_id, severity, revenue_impact, description)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_detections)
    
    conn.commit()
    conn.close()
    print("✓ Created sample data")

def main():
    """Main setup function."""
    print("🚀 Setting up Revenue Leakage Detection System...")
    print("=" * 50)
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            sys.exit(1)
        
        print(f"✓ Python version: {sys.version}")
        
        # Create directories
        create_directories()
        
        # Create configuration
        create_sample_env()
        
        # Create database
        create_sample_database()
        
        # Create sample data
        create_sample_data()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit the .env file with your configuration")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the web application: python web/app.py")
        print("4. Open http://127.0.0.1:5000 in your browser")
        print("\n📚 Documentation:")
        print("- API Documentation: docs/API.md")
        print("- Deployment Guide: docs/DEPLOYMENT.md")
        print("- Development Roadmap: ROADMAP.md")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
