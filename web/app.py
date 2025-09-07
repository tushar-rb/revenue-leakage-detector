#!/usr/bin/env python3
"""
Revenue Leakage Detection System - Web Dashboard

This Flask web application provides:
- Real-time monitoring dashboard
- Interactive reports and visualizations
- Investigation ticket management
- Executive summary views
- System status and performance metrics
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
from pathlib import Path
import sys
import os
import plotly
import plotly.express as px
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import RevenueLeakageDetectionSystem
try:
    from utils.formatting import (
        format_indian_currency, 
        format_indian_number_words, 
        currency_filter, 
        currency_short_filter,
        number_format_filter
    )
    from utils.file_processor import FileProcessor, create_sample_upload_data
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Fallback functions
    def format_indian_currency(amount, include_symbol=True):
        symbol = "₹" if include_symbol else ""
        return f"{symbol}{amount:,.2f}"
    
    def format_indian_number_words(amount):
        return f"₹{amount:,.0f}"
    
    currency_filter = format_indian_currency
    currency_short_filter = format_indian_number_words
    number_format_filter = lambda x: format_indian_currency(x, False)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'revenue-leakage-detector-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = str(Path(__file__).parent.parent / 'uploads')

# Register Jinja2 filters for Indian formatting
app.jinja_env.filters['currency'] = currency_filter
app.jinja_env.filters['currency_short'] = currency_short_filter
app.jinja_env.filters['number_format'] = number_format_filter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global system instance
system_instance = None
data_dir = Path(__file__).parent.parent / 'data'

# Initialize file processor
if UTILS_AVAILABLE:
    file_processor = FileProcessor(app.config['UPLOAD_FOLDER'])
else:
    file_processor = None

def get_database_connection():
    """Get SQLite database connection"""
    db_path = data_dir / 'processed' / 'revenue_data.db'
    return sqlite3.connect(db_path)

def load_data_from_db(table_name: str) -> pd.DataFrame:
    """Load data from database"""
    try:
        with get_database_connection() as conn:
            return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except Exception as e:
        logger.error(f"Failed to load {table_name}: {str(e)}")
        return pd.DataFrame()

def get_system_metrics():
    """Get current system metrics"""
    try:
        # Load detection data
        detections_df = load_data_from_db('audit_detections')
        tickets_df = load_data_from_db('investigation_tickets')
        
        if detections_df.empty:
            return {
                'total_detections': 0,
                'total_estimated_loss': 0,
                'critical_issues': 0,
                'tickets_created': 0,
                'last_analysis': 'Never',
                'system_status': 'No Data'
            }
        
        metrics = {
            'total_detections': len(detections_df),
            'total_estimated_loss': detections_df['estimated_loss'].sum(),
            'critical_issues': len(detections_df[detections_df['severity'] == 'CRITICAL']),
            'tickets_created': len(tickets_df) if not tickets_df.empty else 0,
            'last_analysis': detections_df['detection_timestamp'].max() if 'detection_timestamp' in detections_df.columns else 'Unknown',
            'system_status': 'Active'
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        return {
            'total_detections': 0,
            'total_estimated_loss': 0,
            'critical_issues': 0,
            'tickets_created': 0,
            'last_analysis': 'Error',
            'system_status': 'Error'
        }

def create_visualizations():
    """Create plotly visualizations for the dashboard"""
    try:
        detections_df = load_data_from_db('audit_detections')
        
        if detections_df.empty:
            return {
                'leakage_by_type': {},
                'severity_distribution': {},
                'financial_impact': {},
                'timeline': {}
            }
        
        # Import formatting utilities
        try:
            from utils.formatting import format_indian_currency, format_indian_number_words
        except ImportError:
            # Fallback functions
            def format_indian_currency(amount, include_symbol=True):
                symbol = "₹" if include_symbol else ""
                return f"{symbol}{amount:,.2f}"
            
            def format_indian_number_words(amount):
                return f"₹{amount:,.0f}"
        
        # Leakage by type
        type_summary = detections_df.groupby('leakage_type').agg({
            'estimated_loss': 'sum',
            'detection_id': 'count'
        }).reset_index()
        
        # Format the estimated loss values for display
        type_summary['formatted_loss'] = type_summary['estimated_loss'].apply(
            lambda x: format_indian_currency(x)
        )
        
        fig_type = px.bar(
            type_summary, 
            x='leakage_type', 
            y='estimated_loss',
            title='Revenue Leakage by Type',
            labels={'estimated_loss': 'Estimated Loss (₹)', 'leakage_type': 'Leakage Type'},
            hover_data={'formatted_loss': True}
        )
        
        # Severity distribution
        severity_counts = detections_df['severity'].value_counts()
        fig_severity = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title='Cases by Severity Level'
        )
        
        # Financial impact over time (if timestamp available)
        if 'detection_timestamp' in detections_df.columns:
            detections_df['detection_date'] = pd.to_datetime(detections_df['detection_timestamp']).dt.date
            daily_impact = detections_df.groupby('detection_date')['estimated_loss'].sum().reset_index()
            
            # Format the daily impact values for display
            daily_impact['formatted_loss'] = daily_impact['estimated_loss'].apply(
                lambda x: format_indian_currency(x)
            )
            
            fig_timeline = px.line(
                daily_impact,
                x='detection_date',
                y='estimated_loss',
                title='Daily Revenue Leakage Detection',
                labels={'estimated_loss': 'Estimated Loss (₹)', 'detection_date': 'Date'},
                hover_data={'formatted_loss': True}
            )
        else:
            fig_timeline = px.bar(x=[1], y=[0], title='Timeline Data Not Available')
        
        # Top financial impacts
        top_impacts = detections_df.nlargest(10, 'estimated_loss')[['customer_id', 'leakage_type', 'estimated_loss']]
        
        # Format the top impact values for display
        top_impacts['formatted_loss'] = top_impacts['estimated_loss'].apply(
            lambda x: format_indian_currency(x)
        )
        
        fig_impact = px.bar(
            top_impacts,
            x='customer_id',
            y='estimated_loss',
            color='leakage_type',
            title='Top 10 Revenue Leakage Cases by Financial Impact',
            labels={'estimated_loss': 'Estimated Loss (₹)'},
            hover_data={'formatted_loss': True}
        )
        
        return {
            'leakage_by_type': json.dumps(fig_type, cls=PlotlyJSONEncoder),
            'severity_distribution': json.dumps(fig_severity, cls=PlotlyJSONEncoder),
            'financial_impact': json.dumps(fig_impact, cls=PlotlyJSONEncoder),
            'timeline': json.dumps(fig_timeline, cls=PlotlyJSONEncoder)
        }
        
    except Exception as e:
        logger.error(f"Failed to create visualizations: {str(e)}")
        return {
            'leakage_by_type': {},
            'severity_distribution': {},
            'financial_impact': {},
            'timeline': {}
        }

@app.route('/')
def dashboard():
    """Main dashboard view"""
    metrics = get_system_metrics()
    charts = create_visualizations()
    
    return render_template('dashboard.html', metrics=metrics, charts=charts)


@app.route('/enhanced')
def enhanced_dashboard():
    """Enhanced dashboard view with Indian formatting and interactive features"""
    metrics = get_system_metrics()
    charts = create_visualizations()
    
    return render_template('dashboard_enhanced.html', metrics=metrics, charts=charts)

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for system metrics"""
    return jsonify(get_system_metrics())

@app.route('/api/detections')
def api_detections():
    """API endpoint for detection data"""
    try:
        detections_df = load_data_from_db('audit_detections')
        
        if detections_df.empty:
            return jsonify([])
        
        # Convert to records for JSON serialization
        detections = detections_df.to_dict('records')
        
        # Limit to recent detections for performance
        if len(detections) > 100:
            detections = detections[:100]
        
        return jsonify(detections)
        
    except Exception as e:
        logger.error(f"API detections error: {str(e)}")
        return jsonify([])

@app.route('/api/tickets')
def api_tickets():
    """API endpoint for investigation tickets"""
    try:
        tickets_df = load_data_from_db('investigation_tickets')
        
        if tickets_df.empty:
            return jsonify([])
        
        # Parse investigation_steps from JSON string
        if 'investigation_steps' in tickets_df.columns:
            tickets_df['investigation_steps'] = tickets_df['investigation_steps'].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x
            )
        
        tickets = tickets_df.to_dict('records')
        
        return jsonify(tickets)
        
    except Exception as e:
        logger.error(f"API tickets error: {str(e)}")
        return jsonify([])

@app.route('/api/run-analysis', methods=['POST'])
def api_run_analysis():
    """API endpoint to trigger analysis"""
    global system_instance
    
    try:
        logger.info("Starting revenue leakage analysis via API...")
        
        # Get configuration from request
        config = request.get_json() or {}
        confidence_threshold = config.get('confidence_threshold', 0.7)
        
        # Initialize system
        system_instance = RevenueLeakageDetectionSystem(
            data_dir=str(data_dir),
            config={'confidence_threshold': confidence_threshold}
        )
        
        # Run analysis
        results = system_instance.run_complete_pipeline()
        summary = system_instance.get_results_summary()
        
        return jsonify({
            'status': 'success',
            'message': 'Analysis completed successfully',
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/reports')
def reports():
    """Reports view"""
    try:
        # Get latest executive report
        reports_dir = data_dir / 'reports'
        exec_reports = list(reports_dir.glob('executive_report_*.json'))
        
        latest_report = None
        if exec_reports:
            latest_report_file = max(exec_reports, key=os.path.getctime)
            with open(latest_report_file, 'r') as f:
                latest_report = json.load(f)
        
        # Get tickets summary
        tickets_df = load_data_from_db('investigation_tickets')
        tickets_summary = {
            'total': len(tickets_df) if not tickets_df.empty else 0,
            'critical': len(tickets_df[tickets_df['priority'] == 'CRITICAL']) if not tickets_df.empty else 0,
            'high': len(tickets_df[tickets_df['priority'] == 'HIGH']) if not tickets_df.empty else 0
        }
        
        return render_template('reports.html', 
                             executive_report=latest_report,
                             tickets_summary=tickets_summary)
        
    except Exception as e:
        logger.error(f"Reports view error: {str(e)}")
        return render_template('reports.html', 
                             executive_report=None,
                             tickets_summary={'total': 0, 'critical': 0, 'high': 0})

@app.route('/analytics')
def analytics():
    """Analytics view"""
    try:
        # Get analytics data
        detections_df = load_data_from_db('audit_detections')
        tickets_df = load_data_from_db('investigation_tickets')
        
        analytics_data = {
            'total_detections': len(detections_df) if not detections_df.empty else 0,
            'critical_issues': len(detections_df[detections_df['severity'] == 'critical']) if not detections_df.empty else 0,
            'high_issues': len(detections_df[detections_df['severity'] == 'high']) if not detections_df.empty else 0,
            'medium_issues': len(detections_df[detections_df['severity'] == 'medium']) if not detections_df.empty else 0,
            'total_revenue_impact': float(detections_df['revenue_impact'].sum()) if not detections_df.empty else 0.0,
            'total_tickets': len(tickets_df) if not tickets_df.empty else 0,
        }
        
        # Create charts for analytics
        charts = create_visualizations()
        
        return render_template('analytics.html', analytics=analytics_data, charts=charts)
        
    except Exception as e:
        logger.error(f"Analytics view error: {str(e)}")
        return render_template('analytics.html', analytics={}, charts={})

@app.route('/tickets')
def tickets():
    """Investigation tickets view"""
    try:
        tickets_df = load_data_from_db('investigation_tickets')
        
        if tickets_df.empty:
            tickets_data = []
        else:
            tickets_data = tickets_df.to_dict('records')
            
            # Parse JSON fields
            for ticket in tickets_data:
                if 'investigation_steps' in ticket and isinstance(ticket['investigation_steps'], str):
                    try:
                        ticket['investigation_steps'] = json.loads(ticket['investigation_steps'])
                    except:
                        ticket['investigation_steps'] = []
        
        return render_template('tickets.html', tickets=tickets_data)
        
    except Exception as e:
        logger.error(f"Tickets view error: {str(e)}")
        return render_template('tickets.html', tickets=[])

@app.route('/api/ticket/<ticket_id>/update', methods=['POST'])
def api_update_ticket(ticket_id):
    """Update ticket status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE investigation_tickets SET status = ? WHERE ticket_id = ?",
                (new_status, ticket_id)
            )
            conn.commit()
        
        return jsonify({'status': 'success', 'message': 'Ticket updated'})
        
    except Exception as e:
        logger.error(f"Ticket update error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/generate-sample-data')
def generate_sample_data():
    """Generate sample data via web interface"""
    try:
        import subprocess
        
        # Run sample data generation script
        script_path = Path(__file__).parent.parent / 'scripts' / 'generate_sample_data.py'
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': 'Sample data generated successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate sample data',
                'error': result.stderr
            }), 500
            
    except Exception as e:
        logger.error(f"Sample data generation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/analytics')
def api_analytics():
    """Analytics endpoint for dashboard metrics"""
    try:
        # Get detections data
        detections_df = load_data_from_db('audit_detections')
        tickets_df = load_data_from_db('investigation_tickets')
        
        analytics = {
            'total_detections': len(detections_df) if not detections_df.empty else 0,
            'critical_issues': len(detections_df[detections_df['severity'] == 'critical']) if not detections_df.empty else 0,
            'high_issues': len(detections_df[detections_df['severity'] == 'high']) if not detections_df.empty else 0,
            'medium_issues': len(detections_df[detections_df['severity'] == 'medium']) if not detections_df.empty else 0,
            'total_revenue_impact': float(detections_df['revenue_impact'].sum()) if not detections_df.empty else 0.0,
            'total_tickets': len(tickets_df) if not tickets_df.empty else 0,
            'open_tickets': len(tickets_df[tickets_df['status'] == 'Open']) if not tickets_df.empty else 0,
            'closed_tickets': len(tickets_df[tickets_df['status'] == 'Closed']) if not tickets_df.empty else 0,
            'in_progress_tickets': len(tickets_df[tickets_df['status'] == 'In Progress']) if not tickets_df.empty else 0,
        }
        
        # Add detection types breakdown
        if not detections_df.empty:
            detection_types = detections_df['detection_type'].value_counts().to_dict()
            analytics['detection_types'] = detection_types
        else:
            analytics['detection_types'] = {}
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Analytics API error: {str(e)}")
        return jsonify({
            'total_detections': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'total_revenue_impact': 0.0,
            'total_tickets': 0,
            'open_tickets': 0,
            'closed_tickets': 0,
            'in_progress_tickets': 0,
            'detection_types': {}
        })

@app.route('/api/executive-report')
def api_executive_report():
    """Executive report API endpoint"""
    try:
        # Get latest executive report
        reports_dir = data_dir / 'reports'
        exec_reports = list(reports_dir.glob('executive_report_*.json'))
        
        if not exec_reports:
            return jsonify({
                'error': 'No executive reports available. Please run analysis first.'
            })
        
        # Get the latest report
        latest_report_file = max(exec_reports, key=os.path.getctime)
        with open(latest_report_file, 'r') as f:
            report_data = json.load(f)
        
        return jsonify(report_data)
        
    except Exception as e:
        logger.error(f"Executive report API error: {str(e)}")
        return jsonify({
            'error': f'Error loading executive report: {str(e)}'
        })

@app.route('/api/executive-report/download')
def api_executive_report_download():
    """Download executive report"""
    try:
        # Get latest executive report
        reports_dir = data_dir / 'reports'
        exec_reports = list(reports_dir.glob('executive_report_*.json'))
        
        if not exec_reports:
            return jsonify({'error': 'No reports available'}), 404
        
        latest_report_file = max(exec_reports, key=os.path.getctime)
        return send_file(
            latest_report_file,
            as_attachment=True,
            download_name=f'executive_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
    except Exception as e:
        logger.error(f"Executive report download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    """Generate a new report"""
    try:
        request_data = request.get_json() or {}
        report_type = request_data.get('type', 'executive')
        date_range = request_data.get('date_range', '30')
        
        # For now, we'll trigger a new analysis to generate fresh reports
        global system_instance
        
        if not system_instance:
            system_instance = RevenueLeakageDetectionSystem(
                data_dir=str(data_dir),
                config={'confidence_threshold': 0.7}
            )
        
        # Run the reporting phase to generate new reports
        results = system_instance.run_complete_pipeline()
        
        return jsonify({
            'success': True,
            'message': f'{report_type.title()} report generated successfully',
            'report_type': report_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/upload')
def upload_page():
    """File upload page"""
    try:
        if not UTILS_AVAILABLE:
            return render_template('error.html', 
                                 error_title="Feature Not Available",
                                 error_message="File upload functionality requires additional dependencies.")
        
        sample_data = create_sample_upload_data(file_processor) if file_processor else {}
        
        return render_template('upload.html', sample_data=sample_data)
        
    except Exception as e:
        logger.error(f"Upload page error: {str(e)}")
        return render_template('upload.html', sample_data={})

@app.route('/api/upload', methods=['POST'])
def api_upload_file():
    """Handle file upload and processing"""
    if not UTILS_AVAILABLE or not file_processor:
        return jsonify({
            'success': False,
            'error': 'File upload functionality not available'
        }), 503
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Save uploaded file
        save_result = file_processor.save_uploaded_file(file, secure_filename(file.filename))
        
        if not save_result['success']:
            return jsonify(save_result), 400
        
        # Process the file
        process_result = file_processor.process_file(
            save_result['file_path'], 
            save_result['file_type']
        )
        
        # Combine results
        response_data = {
            **save_result,
            **process_result,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@app.route('/api/upload/list')
def api_list_uploaded_files():
    """List previously uploaded files"""
    if not UTILS_AVAILABLE or not file_processor:
        return jsonify({
            'success': False,
            'error': 'File upload functionality not available'
        })
    
    try:
        uploaded_files = []
        upload_dir = Path(file_processor.upload_dir)
        
        for file_type_dir in upload_dir.iterdir():
            if file_type_dir.is_dir():
                for file_path in file_type_dir.iterdir():
                    if file_path.is_file():
                        stat = file_path.stat()
                        uploaded_files.append({
                            'filename': file_path.name,
                            'file_type': file_type_dir.name,
                            'size': stat.st_size,
                            'uploaded': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'path': str(file_path)
                        })
        
        # Sort by upload time (newest first)
        uploaded_files.sort(key=lambda x: x['uploaded'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': uploaded_files[:50],  # Limit to 50 most recent files
            'total_count': len(uploaded_files)
        })
        
    except Exception as e:
        logger.error(f"List uploaded files error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system': 'Revenue Leakage Detection System',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_title="Page Not Found",
                         error_message="The requested page could not be found."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_title="Internal Server Error", 
                         error_message="An internal server error occurred."), 500

if __name__ == '__main__':
    # Ensure data directories exist
    data_dir.mkdir(exist_ok=True)
    (data_dir / 'processed').mkdir(exist_ok=True)
    (data_dir / 'reports').mkdir(exist_ok=True)
    (data_dir / 'sample').mkdir(exist_ok=True)
    
    logger.info("Starting Revenue Leakage Detection Web Dashboard...")
    logger.info(f"Data directory: {data_dir}")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True
    )
