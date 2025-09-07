# Revenue Leakage Detection System - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the AI-Powered Revenue Leakage Detection System in production environments. The system supports various deployment options from single-server installations to highly available cloud deployments.

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores, 2.4 GHz
- **RAM**: 8 GB
- **Storage**: 100 GB SSD
- **OS**: Ubuntu 20.04 LTS, RHEL 8+, or Windows Server 2019+
- **Python**: 3.8 or higher
- **Database**: PostgreSQL 12+ or SQLite (for development)

### Recommended Production Requirements
- **CPU**: 8 cores, 3.0 GHz
- **RAM**: 32 GB
- **Storage**: 500 GB SSD with backup storage
- **Network**: 1 Gbps connection
- **Load Balancer**: Nginx or HAProxy
- **Database**: PostgreSQL 14+ with replication
- **Monitoring**: Prometheus + Grafana

### Supported Platforms
- **Cloud**: AWS, Azure, Google Cloud Platform
- **Containers**: Docker, Kubernetes
- **Operating Systems**: Linux (Ubuntu, RHEL, CentOS), Windows Server
- **Databases**: PostgreSQL, MySQL, SQLite, MongoDB

## Pre-Deployment Checklist

### Infrastructure Preparation
- [ ] Provision servers/cloud instances
- [ ] Configure network security groups/firewalls
- [ ] Set up SSL certificates
- [ ] Configure DNS records
- [ ] Prepare backup storage
- [ ] Set up monitoring infrastructure

### Software Prerequisites
- [ ] Python 3.8+ installed
- [ ] Database server configured
- [ ] Web server/load balancer configured
- [ ] Required Python packages available
- [ ] Environment variables configured
- [ ] Log directories created

## Installation Methods

### 1. Docker Deployment (Recommended)

#### Step 1: Create Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "web.app:app"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=revenue_detector
      - DB_USER=detector_user
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - revenue_network

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=revenue_detector
      - POSTGRES_USER=detector_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - revenue_network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - revenue_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - revenue_network

  monitoring:
    build: ./monitoring
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
    networks:
      - revenue_network

volumes:
  postgres_data:
  redis_data:

networks:
  revenue_network:
    driver: bridge
```

#### Step 2: Configure Environment

**.env:**
```bash
# Database Configuration
DB_PASSWORD=your_secure_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=revenue_detector
DB_USER=detector_user

# Application Configuration
SECRET_KEY=your_application_secret_key
DEBUG=false
LOG_LEVEL=INFO

# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4

# Email Configuration
SMTP_SERVER=smtp.company.com
SMTP_PORT=587
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=your_email_password
ALERT_EMAIL_RECIPIENTS=cfo@company.com,revenue-team@company.com

# Monitoring Configuration
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Security Configuration
ALLOWED_HOSTS=your-domain.com,localhost
CORS_ORIGINS=https://your-domain.com
SSL_REDIRECT=true
```

#### Step 3: Deploy with Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/revenue-leakage-detector.git
cd revenue-leakage-detector

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start the services
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs app

# Run initial setup
docker-compose exec app python scripts/setup_database.py
docker-compose exec app python scripts/generate_sample_data.py
```

### 2. Kubernetes Deployment

#### Step 1: Create Kubernetes Manifests

**namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: revenue-detector
```

**configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: revenue-detector-config
  namespace: revenue-detector
data:
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "revenue_detector"
  REDIS_URL: "redis://redis-service:6379"
  LOG_LEVEL: "INFO"
  DEBUG: "false"
```

**secret.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: revenue-detector-secrets
  namespace: revenue-detector
type: Opaque
data:
  DB_PASSWORD: <base64-encoded-password>
  SECRET_KEY: <base64-encoded-secret>
  OPENAI_API_KEY: <base64-encoded-api-key>
```

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: revenue-detector-app
  namespace: revenue-detector
spec:
  replicas: 3
  selector:
    matchLabels:
      app: revenue-detector-app
  template:
    metadata:
      labels:
        app: revenue-detector-app
    spec:
      containers:
      - name: app
        image: revenue-detector:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: revenue-detector-config
        - secretRef:
            name: revenue-detector-secrets
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: revenue-detector-pvc
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: revenue-detector-service
  namespace: revenue-detector
spec:
  selector:
    app: revenue-detector-app
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: LoadBalancer
```

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: revenue-detector-ingress
  namespace: revenue-detector
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - revenue-detector.company.com
    secretName: revenue-detector-tls
  rules:
  - host: revenue-detector.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: revenue-detector-service
            port:
              number: 80
```

#### Step 2: Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets and configmaps
kubectl apply -f secret.yaml
kubectl apply -f configmap.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get pods -n revenue-detector
kubectl get services -n revenue-detector
kubectl logs -n revenue-detector deployment/revenue-detector-app
```

### 3. Traditional Server Deployment

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.9 python3.9-venv python3.9-dev \
    postgresql-client nginx redis-server git curl

# Create application user
sudo useradd -m -s /bin/bash revenue-detector
sudo mkdir -p /opt/revenue-detector
sudo chown revenue-detector:revenue-detector /opt/revenue-detector
```

#### Step 2: Application Installation

```bash
# Switch to application user
sudo su - revenue-detector

# Clone repository
cd /opt/revenue-detector
git clone https://github.com/your-org/revenue-leakage-detector.git .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn supervisor

# Create configuration
cp config/production.env .env
# Edit .env with production values
```

#### Step 3: System Service Configuration

**systemd service file (/etc/systemd/system/revenue-detector.service):**
```ini
[Unit]
Description=Revenue Leakage Detection System
After=network.target postgresql.service redis.service

[Service]
Type=forking
User=revenue-detector
Group=revenue-detector
WorkingDirectory=/opt/revenue-detector
Environment=PATH=/opt/revenue-detector/venv/bin
ExecStart=/opt/revenue-detector/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --daemon \
    --pid /opt/revenue-detector/gunicorn.pid \
    --access-logfile /var/log/revenue-detector/access.log \
    --error-logfile /var/log/revenue-detector/error.log \
    web.app:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PIDFile=/opt/revenue-detector/gunicorn.pid
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### Step 4: Nginx Configuration

**/etc/nginx/sites-available/revenue-detector:**
```nginx
upstream revenue_detector {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name revenue-detector.company.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name revenue-detector.company.com;

    ssl_certificate /etc/ssl/certs/revenue-detector.crt;
    ssl_certificate_key /etc/ssl/private/revenue-detector.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;
    keepalive_timeout 65;

    access_log /var/log/nginx/revenue-detector-access.log;
    error_log /var/log/nginx/revenue-detector-error.log;

    location / {
        proxy_pass http://revenue_detector;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /static/ {
        alias /opt/revenue-detector/web/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /health {
        proxy_pass http://revenue_detector;
        access_log off;
    }
}
```

## Database Setup

### PostgreSQL Configuration

#### Step 1: Install and Configure PostgreSQL

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

```sql
-- Create database and user
CREATE DATABASE revenue_detector;
CREATE USER detector_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE revenue_detector TO detector_user;

-- Grant necessary permissions
\c revenue_detector
GRANT ALL ON SCHEMA public TO detector_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO detector_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO detector_user;

-- Exit
\q
```

#### Step 2: Optimize PostgreSQL for Production

**/etc/postgresql/14/main/postgresql.conf:**
```conf
# Memory Configuration
shared_buffers = 8GB                    # 25% of RAM
effective_cache_size = 24GB             # 75% of RAM
work_mem = 64MB                         # For complex queries
maintenance_work_mem = 1GB              # For maintenance operations

# Checkpoint Configuration
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB

# Connection Configuration
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# Logging Configuration
log_destination = 'csvlog'
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_min_duration_statement = 1000      # Log slow queries
```

### Database Migration and Setup

```bash
# Run database initialization
python scripts/setup_database.py

# Create initial schema
python -c "
from agents.data_analyst import create_data_analyst_agent
from agents.audit_analyst import create_audit_analyst_agent
from agents.reporting_agent import create_reporting_agent

# This will create necessary tables
agent = create_data_analyst_agent()
"

# Verify database setup
psql -U detector_user -d revenue_detector -c "\dt"
```

## Security Configuration

### SSL/TLS Configuration

#### Step 1: Obtain SSL Certificates

```bash
# Using Let's Encrypt (recommended)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d revenue-detector.company.com

# Or use existing certificates
sudo cp your-certificate.crt /etc/ssl/certs/revenue-detector.crt
sudo cp your-private-key.key /etc/ssl/private/revenue-detector.key
sudo chmod 600 /etc/ssl/private/revenue-detector.key
```

### Firewall Configuration

```bash
# Configure UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Or configure iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
sudo iptables-save > /etc/iptables/rules.v4
```

### Application Security

#### Step 1: Environment Security

```bash
# Secure environment file
sudo chmod 600 /opt/revenue-detector/.env
sudo chown revenue-detector:revenue-detector /opt/revenue-detector/.env

# Create secure directories
sudo mkdir -p /var/log/revenue-detector
sudo chown revenue-detector:revenue-detector /var/log/revenue-detector
sudo chmod 755 /var/log/revenue-detector
```

#### Step 2: Database Security

```bash
# Secure PostgreSQL
sudo -u postgres psql
```

```sql
-- Revoke public access
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE revenue_detector FROM PUBLIC;

-- Create read-only user for monitoring
CREATE USER monitor_user WITH ENCRYPTED PASSWORD 'monitor_password';
GRANT CONNECT ON DATABASE revenue_detector TO monitor_user;
GRANT USAGE ON SCHEMA public TO monitor_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitor_user;
```

## Monitoring and Logging

### Prometheus Configuration

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "revenue_detector_rules.yml"

scrape_configs:
  - job_name: 'revenue-detector'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

**revenue_detector_rules.yml:**
```yaml
groups:
  - name: revenue_detector
    rules:
      - alert: HighCriticalDetections
        expr: revenue_detector_critical_detections > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High number of critical revenue leakage detections"
          description: "{{ $value }} critical detections found in the last 5 minutes"

      - alert: AnalysisFailure
        expr: increase(revenue_detector_analysis_failures[1h]) > 2
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Multiple analysis failures detected"
          description: "Analysis pipeline has failed {{ $value }} times in the last hour"

      - alert: DatabaseConnectionFailure
        expr: revenue_detector_db_connection_failures > 0
        for: 1m
        labels:
          severity: high
        annotations:
          summary: "Database connection failures detected"
          description: "Unable to connect to database"
```

### Grafana Dashboard

Import the provided Grafana dashboard configuration:

```json
{
  "dashboard": {
    "title": "Revenue Leakage Detection System",
    "panels": [
      {
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "revenue_detector_total_detections",
            "legendFormat": "Total Detections"
          },
          {
            "expr": "revenue_detector_critical_detections",
            "legendFormat": "Critical Issues"
          }
        ]
      },
      {
        "title": "Detection Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(revenue_detector_detections_total[5m])",
            "legendFormat": "Detections per second"
          }
        ]
      }
    ]
  }
}
```

### Centralized Logging

#### ELK Stack Configuration

**filebeat.yml:**
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/revenue-detector/*.log
    - /var/log/nginx/revenue-detector-*.log
  fields:
    service: revenue-detector
  multiline.pattern: '^\d{4}-\d{2}-\d{2}'
  multiline.negate: true
  multiline.match: after

output.logstash:
  hosts: ["logstash:5044"]

processors:
- add_host_metadata:
    when.not.contains.tags: forwarded
```

## Backup and Recovery

### Database Backup Strategy

#### Automated Backup Script

```bash
#!/bin/bash
# /opt/revenue-detector/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/revenue-detector"
DB_NAME="revenue_detector"
DB_USER="detector_user"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Application data backup
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz /opt/revenue-detector/data

# Configuration backup
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz /opt/revenue-detector/.env /etc/nginx/sites-available/revenue-detector

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/ s3://your-backup-bucket/revenue-detector/ --recursive
```

#### Cron Job Configuration

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/revenue-detector/scripts/backup.sh

# Weekly full backup on Sundays at 1 AM
0 1 * * 0 /opt/revenue-detector/scripts/full_backup.sh
```

### Recovery Procedures

#### Database Recovery

```bash
# Stop application
sudo systemctl stop revenue-detector

# Restore database
gunzip -c /opt/backups/revenue-detector/db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -U detector_user revenue_detector

# Restore application data
cd /opt/revenue-detector
tar -xzf /opt/backups/revenue-detector/data_backup_YYYYMMDD_HHMMSS.tar.gz --strip-components=3

# Start application
sudo systemctl start revenue-detector
```

## Performance Optimization

### Application Tuning

#### Gunicorn Configuration

```python
# gunicorn_config.py
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True

# Logging
accesslog = "/var/log/revenue-detector/access.log"
errorlog = "/var/log/revenue-detector/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

### Database Optimization

#### Index Creation

```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_audit_detections_customer_id ON audit_detections(customer_id);
CREATE INDEX idx_audit_detections_severity ON audit_detections(severity);
CREATE INDEX idx_audit_detections_timestamp ON audit_detections(detection_timestamp);
CREATE INDEX idx_investigation_tickets_priority ON investigation_tickets(priority);
CREATE INDEX idx_investigation_tickets_status ON investigation_tickets(status);

-- Composite indexes for complex queries
CREATE INDEX idx_detections_customer_severity ON audit_detections(customer_id, severity);
CREATE INDEX idx_tickets_priority_status ON investigation_tickets(priority, status);
```

## Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check logs
sudo journalctl -u revenue-detector -f
tail -f /var/log/revenue-detector/error.log

# Check configuration
python -c "import os; print(os.environ.get('DB_HOST', 'Not set'))"

# Test database connection
python -c "
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    database='revenue_detector',
    user='detector_user',
    password='your_password'
)
print('Database connection successful')
"
```

#### High Memory Usage

```bash
# Monitor memory usage
htop
free -m

# Check for memory leaks
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# Adjust Gunicorn workers if needed
sudo systemctl edit revenue-detector
# Add:
# [Service]
# ExecStart=
# ExecStart=/opt/revenue-detector/venv/bin/gunicorn --config gunicorn_config.py web.app:app
```

#### Database Performance Issues

```sql
-- Check for long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Analyze table statistics
ANALYZE audit_detections;
ANALYZE investigation_tickets;

-- Check index usage
SELECT schemaname,tablename,attname,n_distinct,correlation
FROM pg_stats
WHERE tablename = 'audit_detections';
```

### Health Checks

#### Automated Health Check Script

```bash
#!/bin/bash
# /opt/revenue-detector/scripts/health_check.sh

# Check application response
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $HTTP_STATUS -ne 200 ]; then
    echo "Application health check failed: HTTP $HTTP_STATUS"
    exit 1
fi

# Check database connection
psql -U detector_user -d revenue_detector -c "SELECT 1;" > /dev/null
if [ $? -ne 0 ]; then
    echo "Database connection failed"
    exit 1
fi

# Check disk space
DISK_USAGE=$(df /opt/revenue-detector | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage critical: ${DISK_USAGE}%"
    exit 1
fi

echo "All health checks passed"
exit 0
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Tasks
- Monitor system health and performance metrics
- Review error logs for any issues
- Check backup completion status
- Monitor disk space usage

#### Weekly Tasks
- Review and analyze system performance trends
- Update security patches if available
- Clean up old log files and temporary data
- Review and update monitoring alerts

#### Monthly Tasks
- Review and optimize database performance
- Update SSL certificates if needed
- Conduct security audit and review
- Test backup and recovery procedures
- Review and update documentation

### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python dependencies
cd /opt/revenue-detector
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart application
sudo systemctl restart revenue-detector
sudo systemctl restart nginx

# Verify everything is working
curl -f http://localhost/health
```

## Support and Contact

For deployment assistance and support:

- **Documentation**: [docs.revenue-detector.com](https://docs.revenue-detector.com)
- **Support Email**: support@revenue-detector.com
- **Emergency Contact**: +1-555-REVENUE (24/7)
- **Status Page**: [status.revenue-detector.com](https://status.revenue-detector.com)

Remember to follow your organization's deployment and security policies when implementing this system in production environments.
