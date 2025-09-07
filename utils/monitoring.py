#!/usr/bin/env python3
"""
Real-time Monitoring System for Revenue Leakage Detection

This module provides:
1. Scheduled analysis execution
2. Real-time data monitoring
3. Alert and notification system
4. Performance monitoring
5. System health checks
"""

import time
import threading
import schedule
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Callable, Optional
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import sqlite3
import pandas as pd
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import RevenueLeakageDetectionSystem

class AlertSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MonitoringAlert:
    def __init__(self, severity: str, title: str, message: str, data: Dict = None):
        self.severity = severity
        self.title = title
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
        self.alert_id = f"ALERT_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"

class RealtimeMonitor:
    """
    Real-time monitoring system for revenue leakage detection
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.is_running = False
        self.monitoring_thread = None
        self.scheduler_thread = None
        
        # Alert system
        self.alert_handlers = []
        self.recent_alerts = []
        self.max_recent_alerts = 100
        
        # Performance tracking
        self.performance_metrics = {}
        self.system_health = {"status": "UNKNOWN", "last_check": None}
        
        # Configuration
        self.data_dir = self.config.get('data_dir', str(Path(__file__).parent.parent / 'data'))
        self.monitoring_interval = self.config.get('monitoring_interval', 300)  # 5 minutes
        self.analysis_schedule = self.config.get('analysis_schedule', 'daily')  # daily, hourly, weekly
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'critical_detections': 5,
            'high_estimated_loss': 10000,
            'system_error_rate': 0.1
        })
        
        self.logger.info("Real-time Monitor initialized")
    
    def add_alert_handler(self, handler: Callable[[MonitoringAlert], None]):
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
        self.logger.info("Alert handler added")
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_running:
            self.logger.warning("Monitor is already running")
            return
        
        self.is_running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Schedule analysis based on configuration
        self._setup_analysis_schedule()
        
        self.logger.info("Real-time monitoring started")
        
        # Send startup alert
        self._send_alert(MonitoringAlert(
            severity=AlertSeverity.LOW,
            title="Monitoring System Started",
            message="Revenue leakage real-time monitoring has been activated.",
            data={"monitoring_interval": self.monitoring_interval}
        ))
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Clear scheduled jobs
        schedule.clear()
        
        self.logger.info("Real-time monitoring stopped")
        
        # Send shutdown alert
        self._send_alert(MonitoringAlert(
            severity=AlertSeverity.LOW,
            title="Monitoring System Stopped",
            message="Revenue leakage real-time monitoring has been deactivated."
        ))
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                self._perform_health_check()
                self._check_system_metrics()
                self._monitor_data_quality()
                self._update_performance_metrics()
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                self._send_alert(MonitoringAlert(
                    severity=AlertSeverity.HIGH,
                    title="Monitoring System Error",
                    message=f"Error in monitoring loop: {str(e)}"
                ))
            
            time.sleep(self.monitoring_interval)
    
    def _scheduler_loop(self):
        """Scheduler loop for scheduled tasks"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
    
    def _setup_analysis_schedule(self):
        """Setup automated analysis schedule"""
        if self.analysis_schedule == 'hourly':
            schedule.every().hour.do(self._run_scheduled_analysis)
            self.logger.info("Scheduled hourly analysis")
        elif self.analysis_schedule == 'daily':
            schedule.every().day.at("02:00").do(self._run_scheduled_analysis)
            self.logger.info("Scheduled daily analysis at 02:00")
        elif self.analysis_schedule == 'weekly':
            schedule.every().monday.at("02:00").do(self._run_scheduled_analysis)
            self.logger.info("Scheduled weekly analysis on Monday at 02:00")
        
        # Also schedule health checks
        schedule.every(10).minutes.do(self._perform_health_check)
        self.logger.info("Scheduled health checks every 10 minutes")
    
    def _run_scheduled_analysis(self):
        """Run scheduled revenue leakage analysis"""
        self.logger.info("Starting scheduled analysis...")
        
        try:
            # Create system instance
            system = RevenueLeakageDetectionSystem(
                data_dir=self.data_dir,
                config=self.config.get('analysis_config', {})
            )
            
            # Run analysis
            start_time = datetime.now()
            results = system.run_complete_pipeline()
            end_time = datetime.now()
            
            # Extract key metrics
            execution_summary = results.get('execution_summary', {})
            success = execution_summary.get('overall_success', False)
            
            if success:
                # Analysis successful - check for alerts
                key_metrics = execution_summary.get('key_metrics', {})
                detections = key_metrics.get('leakage_detections', 0)
                estimated_loss = key_metrics.get('estimated_total_loss', 0)
                critical_issues = key_metrics.get('critical_issues', 0)
                
                # Send success alert
                self._send_alert(MonitoringAlert(
                    severity=AlertSeverity.LOW,
                    title="Scheduled Analysis Completed",
                    message=f"Analysis found {detections} issues with ${estimated_loss:.2f} estimated loss",
                    data=key_metrics
                ))
                
                # Check for critical alerts
                if critical_issues >= self.alert_thresholds.get('critical_detections', 5):
                    self._send_alert(MonitoringAlert(
                        severity=AlertSeverity.CRITICAL,
                        title="Critical Revenue Leakage Detected",
                        message=f"{critical_issues} critical revenue leakage issues detected requiring immediate attention",
                        data=key_metrics
                    ))
                
                if estimated_loss >= self.alert_thresholds.get('high_estimated_loss', 10000):
                    self._send_alert(MonitoringAlert(
                        severity=AlertSeverity.HIGH,
                        title="High Revenue Loss Detected",
                        message=f"Estimated revenue loss of ${estimated_loss:.2f} detected",
                        data=key_metrics
                    ))
                
            else:
                # Analysis failed
                self._send_alert(MonitoringAlert(
                    severity=AlertSeverity.HIGH,
                    title="Scheduled Analysis Failed",
                    message="Scheduled revenue leakage analysis failed to complete successfully"
                ))
            
            # Update performance metrics
            self.performance_metrics['last_analysis'] = {
                'timestamp': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'success': success,
                'results': execution_summary
            }
            
        except Exception as e:
            self.logger.error(f"Scheduled analysis failed: {str(e)}")
            self._send_alert(MonitoringAlert(
                severity=AlertSeverity.HIGH,
                title="Analysis Execution Error",
                message=f"Scheduled analysis failed with error: {str(e)}"
            ))
    
    def _perform_health_check(self):
        """Perform system health check"""
        health_status = "HEALTHY"
        issues = []
        
        try:
            # Check data directory
            data_path = Path(self.data_dir)
            if not data_path.exists():
                issues.append("Data directory not accessible")
                health_status = "UNHEALTHY"
            
            # Check database connectivity
            try:
                db_path = data_path / 'processed' / 'revenue_data.db'
                if db_path.exists():
                    with sqlite3.connect(db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                else:
                    issues.append("Database not found")
                    health_status = "WARNING"
            except Exception as e:
                issues.append(f"Database connectivity issue: {str(e)}")
                health_status = "UNHEALTHY"
            
            # Check disk space (simplified)
            try:
                import shutil
                total, used, free = shutil.disk_usage(data_path)
                free_pct = (free / total) * 100
                if free_pct < 10:
                    issues.append(f"Low disk space: {free_pct:.1f}% free")
                    health_status = "WARNING"
            except:
                pass  # Skip disk check if not available
            
            # Update health status
            self.system_health = {
                "status": health_status,
                "last_check": datetime.now().isoformat(),
                "issues": issues
            }
            
            # Send alert if unhealthy
            if health_status == "UNHEALTHY":
                self._send_alert(MonitoringAlert(
                    severity=AlertSeverity.HIGH,
                    title="System Health Warning",
                    message=f"System health check failed: {'; '.join(issues)}",
                    data=self.system_health
                ))
            
        except Exception as e:
            self.logger.error(f"Health check error: {str(e)}")
            self.system_health = {
                "status": "ERROR",
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _check_system_metrics(self):
        """Check current system metrics for anomalies"""
        try:
            # Load current detection data
            db_path = Path(self.data_dir) / 'processed' / 'revenue_data.db'
            if not db_path.exists():
                return
            
            with sqlite3.connect(db_path) as conn:
                # Check recent detections
                recent_detections = pd.read_sql_query("""
                    SELECT * FROM audit_detections 
                    WHERE detection_timestamp >= datetime('now', '-1 hour')
                """, conn)
                
                if not recent_detections.empty:
                    critical_count = len(recent_detections[recent_detections['severity'] == 'CRITICAL'])
                    total_loss = recent_detections['estimated_loss'].sum()
                    
                    # Alert on significant recent activity
                    if critical_count > 0:
                        self._send_alert(MonitoringAlert(
                            severity=AlertSeverity.MEDIUM,
                            title="Recent Critical Detections",
                            message=f"{critical_count} critical issues detected in the last hour",
                            data={"count": critical_count, "total_loss": total_loss}
                        ))
                
        except Exception as e:
            self.logger.error(f"Metrics check error: {str(e)}")
    
    def _monitor_data_quality(self):
        """Monitor data quality and freshness"""
        try:
            # Check data freshness
            sample_data_path = Path(self.data_dir) / 'sample'
            if sample_data_path.exists():
                latest_file = None
                latest_time = None
                
                for file_path in sample_data_path.glob('*.csv'):
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if latest_time is None or file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path
                
                if latest_time:
                    age_hours = (datetime.now() - latest_time).total_seconds() / 3600
                    
                    # Alert if data is very old (configurable threshold)
                    max_age_hours = self.config.get('max_data_age_hours', 24)
                    if age_hours > max_age_hours:
                        self._send_alert(MonitoringAlert(
                            severity=AlertSeverity.MEDIUM,
                            title="Stale Data Warning",
                            message=f"Data is {age_hours:.1f} hours old, consider refreshing",
                            data={"age_hours": age_hours, "latest_file": str(latest_file)}
                        ))
                
        except Exception as e:
            self.logger.error(f"Data quality monitoring error: {str(e)}")
    
    def _update_performance_metrics(self):
        """Update system performance metrics"""
        self.performance_metrics['system_health'] = self.system_health
        self.performance_metrics['monitoring_uptime'] = {
            'started': getattr(self, 'start_time', datetime.now()).isoformat(),
            'current': datetime.now().isoformat(),
            'is_running': self.is_running
        }
        self.performance_metrics['recent_alerts_count'] = len(self.recent_alerts)
    
    def _send_alert(self, alert: MonitoringAlert):
        """Send alert through configured handlers"""
        # Store in recent alerts
        self.recent_alerts.append(alert)
        if len(self.recent_alerts) > self.max_recent_alerts:
            self.recent_alerts.pop(0)
        
        # Log alert
        log_level = {
            AlertSeverity.LOW: logging.INFO,
            AlertSeverity.MEDIUM: logging.WARNING,
            AlertSeverity.HIGH: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        self.logger.log(log_level, f"ALERT [{alert.severity}] {alert.title}: {alert.message}")
        
        # Send through handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler error: {str(e)}")
    
    def get_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'system_health': self.system_health,
            'performance_metrics': self.performance_metrics,
            'recent_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity,
                    'title': alert.title,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat()
                } for alert in self.recent_alerts[-10:]  # Last 10 alerts
            ],
            'configuration': {
                'monitoring_interval': self.monitoring_interval,
                'analysis_schedule': self.analysis_schedule,
                'alert_thresholds': self.alert_thresholds
            }
        }

# Alert handlers
class EmailAlertHandler:
    """Email alert handler"""
    
    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
        self.logger = logging.getLogger(__name__)
    
    def __call__(self, alert: MonitoringAlert):
        """Send email alert"""
        try:
            if alert.severity in ['HIGH', 'CRITICAL']:  # Only send emails for high severity
                self._send_email(alert)
        except Exception as e:
            self.logger.error(f"Email alert handler error: {str(e)}")
    
    def _send_email(self, alert: MonitoringAlert):
        """Send email notification"""
        msg = MimeMultipart()
        msg['From'] = self.smtp_config['sender']
        msg['To'] = ', '.join(self.smtp_config['recipients'])
        msg['Subject'] = f"Revenue Leakage Alert: {alert.title}"
        
        body = f"""
        Alert Details:
        
        Severity: {alert.severity}
        Title: {alert.title}
        Message: {alert.message}
        Timestamp: {alert.timestamp}
        
        Alert ID: {alert.alert_id}
        
        ---
        Revenue Leakage Detection System
        Automated Monitoring Alert
        """
        
        msg.attach(MimeText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
        if self.smtp_config.get('use_tls'):
            server.starttls()
        if self.smtp_config.get('username'):
            server.login(self.smtp_config['username'], self.smtp_config['password'])
        
        server.send_message(msg)
        server.quit()
        
        self.logger.info(f"Email alert sent: {alert.title}")

class WebhookAlertHandler:
    """Webhook alert handler for integrations"""
    
    def __init__(self, webhook_url: str, headers: Dict = None):
        self.webhook_url = webhook_url
        self.headers = headers or {'Content-Type': 'application/json'}
        self.logger = logging.getLogger(__name__)
    
    def __call__(self, alert: MonitoringAlert):
        """Send webhook notification"""
        try:
            import requests
            
            payload = {
                'alert_id': alert.alert_id,
                'severity': alert.severity,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'data': alert.data
            }
            
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Webhook alert sent: {alert.title}")
            else:
                self.logger.warning(f"Webhook alert failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Webhook alert handler error: {str(e)}")

def create_monitor(config: Dict = None) -> RealtimeMonitor:
    """Factory function to create monitoring instance"""
    return RealtimeMonitor(config)

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create monitor with sample configuration
    config = {
        'data_dir': str(Path(__file__).parent.parent / 'data'),
        'monitoring_interval': 60,  # 1 minute for testing
        'analysis_schedule': 'hourly',
        'alert_thresholds': {
            'critical_detections': 3,
            'high_estimated_loss': 5000
        }
    }
    
    monitor = create_monitor(config)
    
    # Add console alert handler
    def console_alert_handler(alert):
        print(f"🚨 ALERT [{alert.severity}] {alert.title}: {alert.message}")
    
    monitor.add_alert_handler(console_alert_handler)
    
    # Start monitoring
    try:
        monitor.start_monitoring()
        print("Real-time monitoring started. Press Ctrl+C to stop.")
        
        # Keep running
        while True:
            time.sleep(10)
            status = monitor.get_status()
            print(f"System Health: {status['system_health']['status']}")
            
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        monitor.stop_monitoring()
        print("Monitoring stopped.")
