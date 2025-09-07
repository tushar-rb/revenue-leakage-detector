# Revenue Leakage Detection System - API Documentation

## Overview

The Revenue Leakage Detection System provides a comprehensive REST API for managing and monitoring revenue assurance operations. The API enables integration with external systems, automation of analysis workflows, and real-time monitoring of revenue leakage detection.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication for development purposes. In production, implement appropriate authentication mechanisms (JWT, API keys, OAuth2).

## API Endpoints

### System Health and Status

#### GET /health
Returns system health status and basic information.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "system": "Revenue Leakage Detection System",
    "version": "1.0.0"
}
```

#### GET /api/metrics
Returns current system metrics and KPIs.

**Response:**
```json
{
    "total_detections": 145,
    "total_estimated_loss": 25750.50,
    "critical_issues": 8,
    "tickets_created": 92,
    "last_analysis": "2024-01-15T08:30:00Z",
    "system_status": "Active"
}
```

### Analysis Operations

#### POST /api/run-analysis
Triggers a complete revenue leakage analysis pipeline.

**Request Body:**
```json
{
    "confidence_threshold": 0.7,
    "analysis_config": {
        "enable_anomaly_detection": true,
        "batch_size": 1000
    }
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Analysis completed successfully",
    "summary": {
        "status": "SUCCESS",
        "execution_time": "45.32 seconds",
        "records_processed": 15420,
        "detections_found": 23,
        "estimated_loss": 5430.25,
        "critical_issues": 3,
        "potential_recovery": 4615.71,
        "execution_id": "REV-EXEC-20240115-103000",
        "timestamp": "2024-01-15T10:30:45Z"
    }
}
```

**Error Response:**
```json
{
    "status": "error",
    "message": "Analysis failed: Database connection error"
}
```

### Data Management

#### GET /api/detections
Retrieves revenue leakage detection records.

**Query Parameters:**
- `limit`: Maximum number of records to return (default: 100)
- `severity`: Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)
- `leakage_type`: Filter by leakage type
- `from_date`: Start date filter (ISO format)
- `to_date`: End date filter (ISO format)

**Example Request:**
```
GET /api/detections?limit=50&severity=HIGH&from_date=2024-01-01T00:00:00Z
```

**Response:**
```json
[
    {
        "detection_id": "MISS_CNT12345678_20240115103045",
        "customer_id": "CUST000001",
        "contract_id": "CNT12345678",
        "leakage_type": "MISSING_CHARGES",
        "severity": "HIGH",
        "confidence": 0.89,
        "estimated_loss": 1250.00,
        "description": "Missing charges detected for Customer 1's Internet service...",
        "mathematical_evidence": "{\"expected_revenue\": 1250.0, \"actual_revenue\": 0.0}",
        "contextual_analysis": "Service is active but not generating revenue",
        "recommended_action": "Generate missing charges and apply to next billing cycle",
        "detection_timestamp": "2024-01-15T10:30:45Z"
    }
]
```

#### GET /api/tickets
Retrieves investigation tickets.

**Query Parameters:**
- `limit`: Maximum number of tickets to return (default: 100)
- `priority`: Filter by priority (LOW, MEDIUM, HIGH, CRITICAL)
- `status`: Filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
- `assigned_team`: Filter by assigned team

**Response:**
```json
[
    {
        "ticket_id": "REV-A1B2C3D4",
        "title": "Missing Charges - Customer CUST000001 - $1250.00 Revenue at Risk",
        "priority": "HIGH",
        "status": "OPEN",
        "assigned_team": "Billing Operations Team",
        "customer_id": "CUST000001",
        "contract_id": "CNT12345678",
        "leakage_type": "MISSING_CHARGES",
        "estimated_loss": 1250.00,
        "description": "Missing charges detected...",
        "investigation_steps": [
            "1. Verify customer service activation status",
            "2. Check billing system configuration for the customer",
            "3. Review contract terms and pricing",
            "4. Generate missing invoices if confirmed",
            "5. Contact customer to explain billing correction"
        ],
        "business_impact": "Material impact requiring immediate attention...",
        "urgency_reason": "Significant revenue at risk",
        "expected_resolution_time": "2-3 business days",
        "created_timestamp": "2024-01-15T10:30:45Z"
    }
]
```

### Ticket Management

#### POST /api/ticket/{ticket_id}/update
Updates ticket status or properties.

**Path Parameters:**
- `ticket_id`: The unique ticket identifier

**Request Body:**
```json
{
    "status": "IN_PROGRESS",
    "assignee": "john.doe@company.com",
    "notes": "Investigation started, reviewing billing system logs"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Ticket updated successfully",
    "ticket_id": "REV-A1B2C3D4"
}
```

#### GET /api/ticket/{ticket_id}
Retrieves detailed information about a specific ticket.

**Response:**
```json
{
    "ticket_id": "REV-A1B2C3D4",
    "title": "Missing Charges - Customer CUST000001",
    "priority": "HIGH",
    "status": "IN_PROGRESS",
    "customer_id": "CUST000001",
    "contract_id": "CNT12345678",
    "leakage_type": "MISSING_CHARGES",
    "estimated_loss": 1250.00,
    "description": "Detailed description...",
    "investigation_steps": [...],
    "business_impact": "Impact assessment...",
    "assigned_team": "Billing Operations Team",
    "assignee": "john.doe@company.com",
    "created_timestamp": "2024-01-15T10:30:45Z",
    "updated_timestamp": "2024-01-15T14:20:30Z",
    "history": [
        {
            "timestamp": "2024-01-15T14:20:30Z",
            "action": "STATUS_CHANGE",
            "old_value": "OPEN",
            "new_value": "IN_PROGRESS",
            "user": "john.doe@company.com",
            "notes": "Investigation started"
        }
    ]
}
```

### Reporting

#### GET /api/reports
Lists available reports.

**Response:**
```json
{
    "executive_reports": [
        {
            "report_id": "EXEC-RPT-20240115-103045",
            "title": "Revenue Leakage Analysis - Executive Report",
            "generated_timestamp": "2024-01-15T10:30:45Z",
            "summary": "23 instances of potential revenue leakage identified...",
            "total_estimated_loss": 5430.25
        }
    ],
    "detailed_reports": [
        {
            "report_id": "DET-RPT-20240115-103045",
            "title": "Detailed Analysis Report",
            "generated_timestamp": "2024-01-15T10:30:45Z",
            "file_path": "/data/reports/detailed_report_20240115_103045.md"
        }
    ]
}
```

#### GET /api/reports/{report_id}
Retrieves a specific report.

**Response:**
```json
{
    "report_id": "EXEC-RPT-20240115-103045",
    "title": "Revenue Leakage Analysis - Executive Report",
    "executive_summary": "Our AI-powered revenue leakage detection system has identified...",
    "key_findings": [
        "Missing Charges represents the highest risk category with $3,250.00 in potential losses",
        "5 critical issues requiring immediate executive attention"
    ],
    "financial_impact": {
        "immediate_loss": 5430.25,
        "quarterly_projection": 16290.75,
        "annual_projection": 65163.00,
        "recovery_potential": 4615.71
    },
    "risk_assessment": "MEDIUM RISK: Notable revenue gaps requiring systematic resolution",
    "recommendations": [
        "Immediate action required: Address 5 critical issues within 24 hours",
        "Implement automated billing completeness checks"
    ],
    "next_steps": [
        "Review and approve investigation ticket assignments",
        "Monitor critical case resolution within 24-hour SLA"
    ],
    "generated_timestamp": "2024-01-15T10:30:45Z"
}
```

### Data Import/Export

#### POST /api/data/import
Imports data for analysis.

**Request Body (multipart/form-data):**
- `billing_data`: CSV file with billing records
- `contracts`: CSV file with contract data
- `usage_logs`: CSV file with usage data
- `provisioning`: CSV file with provisioning records

**Response:**
```json
{
    "status": "success",
    "message": "Data imported successfully",
    "summary": {
        "billing_records": 1250,
        "contracts": 890,
        "usage_records": 15420,
        "provisioning_records": 2340
    }
}
```

#### GET /api/data/export
Exports analysis results.

**Query Parameters:**
- `format`: Export format (json, csv, excel)
- `data_type`: Type of data to export (detections, tickets, reports)
- `date_range`: Date range for export

**Response:**
- Returns file download or JSON data based on format

### Monitoring and Alerts

#### GET /api/monitoring/status
Returns real-time monitoring status.

**Response:**
```json
{
    "is_running": true,
    "system_health": {
        "status": "HEALTHY",
        "last_check": "2024-01-15T10:25:00Z",
        "issues": []
    },
    "performance_metrics": {
        "last_analysis": {
            "timestamp": "2024-01-15T08:30:00Z",
            "duration_seconds": 45.32,
            "success": true
        },
        "monitoring_uptime": {
            "started": "2024-01-15T00:00:00Z",
            "current": "2024-01-15T10:30:00Z",
            "is_running": true
        }
    },
    "recent_alerts": [
        {
            "alert_id": "ALERT_20240115_082500",
            "severity": "MEDIUM",
            "title": "Recent Critical Detections",
            "message": "3 critical issues detected in the last hour",
            "timestamp": "2024-01-15T08:25:00Z"
        }
    ],
    "configuration": {
        "monitoring_interval": 300,
        "analysis_schedule": "daily",
        "alert_thresholds": {
            "critical_detections": 5,
            "high_estimated_loss": 10000
        }
    }
}
```

#### POST /api/monitoring/configure
Updates monitoring configuration.

**Request Body:**
```json
{
    "monitoring_interval": 600,
    "analysis_schedule": "hourly",
    "alert_thresholds": {
        "critical_detections": 3,
        "high_estimated_loss": 5000
    },
    "notification_settings": {
        "email_enabled": true,
        "webhook_url": "https://your-system.com/webhook"
    }
}
```

### Utility Endpoints

#### POST /generate-sample-data
Generates sample data for testing and demonstration.

**Response:**
```json
{
    "status": "success",
    "message": "Sample data generated successfully",
    "output": "Generated 1000 customers, 1500 contracts, 25000 usage records..."
}
```

## Error Handling

### Standard Error Response Format

```json
{
    "error": {
        "code": "ANALYSIS_FAILED",
        "message": "Analysis pipeline failed at audit stage",
        "details": "Database connection timeout after 30 seconds",
        "timestamp": "2024-01-15T10:30:45Z",
        "request_id": "req_1234567890"
    }
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: System maintenance

### Error Codes

| Code | Description |
|------|-------------|
| `ANALYSIS_FAILED` | Analysis pipeline execution failed |
| `DATA_VALIDATION_ERROR` | Input data validation failed |
| `DATABASE_ERROR` | Database operation failed |
| `AUTHENTICATION_REQUIRED` | Valid authentication required |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | Requested resource does not exist |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `SYSTEM_MAINTENANCE` | System under maintenance |

## Rate Limiting

API requests are rate-limited to ensure system stability:

- **Default**: 100 requests per minute per IP
- **Analysis operations**: 10 requests per hour per IP
- **Data import**: 5 requests per hour per IP

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## WebSocket API (Real-time Updates)

### Connection
```javascript
ws://localhost:8000/ws/monitoring
```

### Message Types

#### System Metrics Update
```json
{
    "type": "metrics_update",
    "data": {
        "total_detections": 145,
        "critical_issues": 8,
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

#### New Detection Alert
```json
{
    "type": "new_detection",
    "data": {
        "detection_id": "MISS_CNT12345678_20240115103045",
        "severity": "HIGH",
        "estimated_loss": 1250.00,
        "customer_id": "CUST000001"
    }
}
```

#### Analysis Status Update
```json
{
    "type": "analysis_status",
    "data": {
        "status": "running",
        "progress": 75,
        "stage": "audit_analysis",
        "estimated_completion": "2024-01-15T10:35:00Z"
    }
}
```

## SDK and Client Libraries

### Python Client
```python
from revenue_detector_client import RevenueDetectorClient

client = RevenueDetectorClient(base_url="http://localhost:8000")

# Run analysis
result = client.run_analysis(confidence_threshold=0.8)

# Get detections
detections = client.get_detections(severity="HIGH", limit=50)

# Update ticket
client.update_ticket("REV-A1B2C3D4", status="RESOLVED")
```

### JavaScript Client
```javascript
import { RevenueDetectorAPI } from 'revenue-detector-js';

const api = new RevenueDetectorAPI('http://localhost:8000');

// Run analysis
const result = await api.runAnalysis({ confidenceThreshold: 0.8 });

// Get detections
const detections = await api.getDetections({ severity: 'HIGH' });

// Real-time monitoring
api.onNewDetection((detection) => {
    console.log('New detection:', detection);
});
```

## Integration Examples

### JIRA Integration
```bash
# Create JIRA ticket from detection
curl -X POST "http://localhost:8000/api/integrations/jira/create-ticket" \
  -H "Content-Type: application/json" \
  -d '{
    "detection_id": "MISS_CNT12345678_20240115103045",
    "jira_project": "REVENUE",
    "assignee": "john.doe@company.com"
  }'
```

### Slack Notification
```bash
# Send Slack alert for critical detections
curl -X POST "http://localhost:8000/api/integrations/slack/notify" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#revenue-alerts",
    "severity_threshold": "HIGH"
  }'
```

### Email Reports
```bash
# Schedule email reports
curl -X POST "http://localhost:8000/api/integrations/email/schedule-report" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["cfo@company.com", "revenue-team@company.com"],
    "schedule": "daily",
    "report_type": "executive_summary"
  }'
```

## Best Practices

### Authentication
- Use API keys for service-to-service communication
- Implement JWT tokens for user sessions
- Rotate API keys regularly

### Performance
- Use pagination for large datasets
- Implement caching for frequently accessed data
- Use WebSocket connections for real-time updates

### Error Handling
- Always check HTTP status codes
- Implement retry logic with exponential backoff
- Log API errors for debugging

### Security
- Use HTTPS in production
- Validate all input parameters
- Implement rate limiting
- Sanitize data before processing

For more information and examples, see the complete API reference and integration guides in the documentation portal.
