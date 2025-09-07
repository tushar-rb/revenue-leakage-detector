#!/usr/bin/env python3
"""
AI-Powered Revenue Leakage Detection System - Main Application

This application orchestrates the three specialized AI agents:
1. Data Analyst Agent (MUSCLE) - Data processing and joining
2. Audit Analyst Agent (MUSCLE + BRAIN) - Revenue leakage detection
3. Reporting Agent (BRAIN) - Intelligent reporting and ticket generation

The system provides a complete end-to-end pipeline for automated revenue
assurance and leakage detection.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import argparse

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.data_analyst import create_data_analyst_agent, DataAnalystAgent
from agents.audit_analyst import create_audit_analyst_agent, AuditAnalystAgent
from agents.reporting_agent import create_reporting_agent, ReportingAgent

class RevenueLeakageDetectionSystem:
    """
    Main system orchestrator for AI-powered revenue leakage detection
    
    This class coordinates the three agent pipeline:
    MUSCLE (Data) -> MUSCLE+BRAIN (Audit) -> BRAIN (Reporting)
    """
    
    def __init__(self, data_dir: Optional[str] = None, config: Optional[Dict] = None):
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir or str(project_root / 'data')
        self.config = config or {}
        
        # Initialize agents
        self.data_analyst: Optional[DataAnalystAgent] = None
        self.audit_analyst: Optional[AuditAnalystAgent] = None
        self.reporting_agent: Optional[ReportingAgent] = None
        
        # Results storage
        self.results = {
            'data_analysis': None,
            'audit_detections': None,
            'reports_and_tickets': None,
            'execution_summary': {}
        }
        
        self.logger.info("🚀 Revenue Leakage Detection System initialized")
    
    def initialize_agents(self):
        """Initialize all three AI agents"""
        self.logger.info("🤖 Initializing AI agents...")
        
        try:
            # Initialize Data Analyst Agent (MUSCLE)
            self.data_analyst = create_data_analyst_agent(data_dir=self.data_dir)
            self.logger.info("  ✅ Data Analyst Agent (MUSCLE) initialized")
            
            # Initialize Audit Analyst Agent (MUSCLE + BRAIN)
            confidence_threshold = self.config.get('confidence_threshold', 0.7)
            self.audit_analyst = create_audit_analyst_agent(
                data_dir=self.data_dir, 
                confidence_threshold=confidence_threshold
            )
            self.logger.info("  ✅ Audit Analyst Agent (MUSCLE + BRAIN) initialized")
            
            # Initialize Reporting Agent (BRAIN)
            self.reporting_agent = create_reporting_agent(data_dir=self.data_dir)
            self.logger.info("  ✅ Reporting Agent (BRAIN) initialized")
            
            self.logger.info("🤖 All AI agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    def run_data_analysis(self) -> bool:
        """Execute Data Analyst Agent (MUSCLE) pipeline"""
        self.logger.info("💪 PHASE 1: Data Analysis (MUSCLE) - Starting...")
        
        try:
            if not self.data_analyst:
                raise ValueError("Data Analyst Agent not initialized")
            
            # Run full data analysis pipeline
            joined_data, summary = self.data_analyst.run_full_analysis()
            
            # Store results
            self.results['data_analysis'] = {
                'joined_data': joined_data,
                'summary': summary,
                'timestamp': datetime.now().isoformat(),
                'status': 'SUCCESS'
            }
            
            self.logger.info("💪 PHASE 1: Data Analysis (MUSCLE) - COMPLETED")
            self.logger.info(f"  📊 Processed {len(joined_data):,} records")
            self.logger.info(f"  🔧 Features engineered: {len(joined_data.columns)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"💪 PHASE 1: Data Analysis failed: {str(e)}")
            self.results['data_analysis'] = {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def run_audit_analysis(self) -> bool:
        """Execute Audit Analyst Agent (MUSCLE + BRAIN) pipeline"""
        self.logger.info("🧠💪 PHASE 2: Audit Analysis (MUSCLE + BRAIN) - Starting...")
        
        try:
            if not self.audit_analyst:
                raise ValueError("Audit Analyst Agent not initialized")
            
            # Run full audit analysis pipeline
            detections, summary = self.audit_analyst.run_full_audit()
            
            # Store results
            self.results['audit_detections'] = {
                'detections': detections,
                'summary': summary,
                'timestamp': datetime.now().isoformat(),
                'status': 'SUCCESS'
            }
            
            self.logger.info("🧠💪 PHASE 2: Audit Analysis (MUSCLE + BRAIN) - COMPLETED")
            self.logger.info(f"  🎯 Detections found: {len(detections)}")
            self.logger.info(f"  💰 Total estimated loss: ${sum(d.estimated_loss for d in detections):.2f}")
            self.logger.info(f"  ⚠️  High priority cases: {summary.get('high_priority_count', 0)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"🧠💪 PHASE 2: Audit Analysis failed: {str(e)}")
            self.results['audit_detections'] = {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def run_reporting(self) -> bool:
        """Execute Reporting Agent (BRAIN) pipeline"""
        self.logger.info("🧠 PHASE 3: Intelligent Reporting (BRAIN) - Starting...")
        
        try:
            if not self.reporting_agent:
                raise ValueError("Reporting Agent not initialized")
            
            # Run full reporting pipeline
            tickets, exec_report, summary = self.reporting_agent.run_full_reporting()
            
            # Store results
            self.results['reports_and_tickets'] = {
                'tickets': tickets,
                'executive_report': exec_report,
                'summary': summary,
                'timestamp': datetime.now().isoformat(),
                'status': 'SUCCESS'
            }
            
            self.logger.info("🧠 PHASE 3: Intelligent Reporting (BRAIN) - COMPLETED")
            self.logger.info(f"  🎫 Investigation tickets created: {len(tickets)}")
            self.logger.info(f"  📋 Executive reports generated: 1")
            self.logger.info(f"  🚨 Critical tickets: {summary.get('critical_tickets', 0)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"🧠 PHASE 3: Reporting failed: {str(e)}")
            self.results['reports_and_tickets'] = {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def run_complete_pipeline(self) -> Dict:
        """Execute the complete AI agent pipeline"""
        start_time = datetime.now()
        self.logger.info("🚀 Starting Complete AI-Powered Revenue Leakage Detection Pipeline")
        self.logger.info("="*80)
        
        # Initialize agents
        self.initialize_agents()
        
        # Phase 1: Data Analysis (MUSCLE)
        phase1_success = self.run_data_analysis()
        
        # Phase 2: Audit Analysis (MUSCLE + BRAIN) - only if Phase 1 succeeded
        phase2_success = False
        if phase1_success:
            phase2_success = self.run_audit_analysis()
        else:
            self.logger.warning("🧠💪 PHASE 2: Skipped due to Phase 1 failure")
        
        # Phase 3: Reporting (BRAIN) - only if Phase 2 succeeded
        phase3_success = False
        if phase2_success:
            phase3_success = self.run_reporting()
        else:
            self.logger.warning("🧠 PHASE 3: Skipped due to Phase 2 failure")
        
        # Calculate execution summary
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Generate execution summary
        execution_summary = self.generate_execution_summary(
            start_time, end_time, execution_time,
            phase1_success, phase2_success, phase3_success
        )
        
        self.results['execution_summary'] = execution_summary
        
        # Log final results
        self.log_final_results(execution_summary)
        
        return self.results
    
    def generate_execution_summary(
        self, 
        start_time: datetime, 
        end_time: datetime, 
        execution_time: float,
        phase1_success: bool,
        phase2_success: bool, 
        phase3_success: bool
    ) -> Dict:
        """Generate comprehensive execution summary"""
        
        # Calculate success metrics
        phases_completed = sum([phase1_success, phase2_success, phase3_success])
        overall_success = phase1_success and phase2_success and phase3_success
        
        # Extract key metrics from results
        data_records = 0
        total_detections = 0
        total_estimated_loss = 0.0
        critical_tickets = 0
        
        if self.results.get('data_analysis', {}).get('status') == 'SUCCESS':
            data_summary = self.results['data_analysis'].get('summary', {})
            data_records = data_summary.get('final_joined_records', 0)
        
        if self.results.get('audit_detections', {}).get('status') == 'SUCCESS':
            audit_summary = self.results['audit_detections'].get('summary', {})
            total_detections = audit_summary.get('total_detections', 0)
            total_estimated_loss = audit_summary.get('total_estimated_loss', 0.0)
        
        if self.results.get('reports_and_tickets', {}).get('status') == 'SUCCESS':
            reporting_summary = self.results['reports_and_tickets'].get('summary', {})
            critical_tickets = reporting_summary.get('critical_tickets', 0)
        
        return {
            'execution_id': f"REV-EXEC-{start_time.strftime('%Y%m%d-%H%M%S')}",
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'execution_time_seconds': execution_time,
            'execution_time_formatted': f"{execution_time:.2f} seconds",
            'overall_success': overall_success,
            'phases_completed': f"{phases_completed}/3",
            'phase_results': {
                'data_analysis': 'SUCCESS' if phase1_success else 'FAILED',
                'audit_analysis': 'SUCCESS' if phase2_success else 'FAILED', 
                'reporting': 'SUCCESS' if phase3_success else 'FAILED'
            },
            'key_metrics': {
                'records_processed': data_records,
                'leakage_detections': total_detections,
                'estimated_total_loss': total_estimated_loss,
                'critical_issues': critical_tickets,
                'potential_recovery': total_estimated_loss * 0.85 if total_estimated_loss > 0 else 0
            },
            'system_performance': {
                'records_per_second': data_records / execution_time if execution_time > 0 else 0,
                'detection_rate': (total_detections / data_records * 100) if data_records > 0 else 0
            },
            'next_actions': self.generate_next_actions(overall_success, critical_tickets)
        }
    
    def generate_next_actions(self, overall_success: bool, critical_tickets: int) -> list:
        """Generate intelligent next actions based on results"""
        actions = []
        
        if not overall_success:
            actions.append("Review system logs for pipeline failures")
            actions.append("Check data source availability and quality")
            actions.append("Verify system configuration and dependencies")
        else:
            if critical_tickets > 0:
                actions.append(f"URGENT: Address {critical_tickets} critical revenue leakage tickets immediately")
                actions.append("Notify executive team of high-priority findings")
            
            actions.append("Review investigation tickets and assign to appropriate teams")
            actions.append("Monitor ticket resolution progress and SLAs")
            actions.append("Schedule follow-up analysis for continuous monitoring")
            actions.append("Update revenue assurance KPIs and dashboards")
        
        return actions
    
    def log_final_results(self, execution_summary: Dict):
        """Log comprehensive final results"""
        self.logger.info("="*80)
        self.logger.info("🎯 AI-POWERED REVENUE LEAKAGE DETECTION - FINAL RESULTS")
        self.logger.info("="*80)
        
        # Execution Summary
        self.logger.info(f"Execution ID: {execution_summary['execution_id']}")
        self.logger.info(f"Total Execution Time: {execution_summary['execution_time_formatted']}")
        self.logger.info(f"Pipeline Success: {'✅ COMPLETE' if execution_summary['overall_success'] else '❌ PARTIAL/FAILED'}")
        self.logger.info(f"Phases Completed: {execution_summary['phases_completed']}")
        
        # Key Metrics
        metrics = execution_summary['key_metrics']
        self.logger.info(f"\n📊 KEY METRICS:")
        self.logger.info(f"  Records Processed: {metrics['records_processed']:,}")
        self.logger.info(f"  Revenue Leakage Detections: {metrics['leakage_detections']:,}")
        self.logger.info(f"  Total Estimated Loss: ${metrics['estimated_total_loss']:,.2f}")
        self.logger.info(f"  Critical Issues: {metrics['critical_issues']}")
        self.logger.info(f"  Potential Recovery: ${metrics['potential_recovery']:,.2f}")
        
        # Performance Metrics
        performance = execution_summary['system_performance']
        self.logger.info(f"\n⚡ PERFORMANCE METRICS:")
        self.logger.info(f"  Processing Speed: {performance['records_per_second']:,.0f} records/second")
        self.logger.info(f"  Detection Rate: {performance['detection_rate']:.2f}%")
        
        # Next Actions
        self.logger.info(f"\n🎯 NEXT ACTIONS:")
        for i, action in enumerate(execution_summary['next_actions'], 1):
            self.logger.info(f"  {i}. {action}")
        
        self.logger.info("="*80)
        
        if execution_summary['overall_success']:
            self.logger.info("✅ Revenue leakage detection pipeline completed successfully!")
            if metrics['critical_issues'] > 0:
                self.logger.warning(f"⚠️  ATTENTION: {metrics['critical_issues']} critical issues require immediate action")
        else:
            self.logger.error("❌ Pipeline completed with errors - review logs for details")
        
        self.logger.info("="*80)
    
    def get_results_summary(self) -> Dict:
        """Get simplified results summary for API/web interface"""
        execution_summary = self.results.get('execution_summary', {})
        
        return {
            'status': 'SUCCESS' if execution_summary.get('overall_success') else 'FAILED',
            'execution_time': execution_summary.get('execution_time_formatted', 'N/A'),
            'records_processed': execution_summary.get('key_metrics', {}).get('records_processed', 0),
            'detections_found': execution_summary.get('key_metrics', {}).get('leakage_detections', 0),
            'estimated_loss': execution_summary.get('key_metrics', {}).get('estimated_total_loss', 0),
            'critical_issues': execution_summary.get('key_metrics', {}).get('critical_issues', 0),
            'potential_recovery': execution_summary.get('key_metrics', {}).get('potential_recovery', 0),
            'execution_id': execution_summary.get('execution_id', 'N/A'),
            'timestamp': execution_summary.get('end_time', datetime.now().isoformat())
        }

def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """Configure logging for the application"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main application entry point"""
    
    parser = argparse.ArgumentParser(
        description="AI-Powered Revenue Leakage Detection System"
    )
    parser.add_argument(
        '--data-dir', 
        type=str, 
        help='Directory containing data files'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO',
        help='Logging level'
    )
    parser.add_argument(
        '--log-file', 
        type=str, 
        help='Log file path'
    )
    parser.add_argument(
        '--confidence-threshold', 
        type=float, 
        default=0.7,
        help='Confidence threshold for detections (0.0-1.0)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Create system configuration
    config = {
        'confidence_threshold': args.confidence_threshold
    }
    
    try:
        # Initialize and run the system
        system = RevenueLeakageDetectionSystem(
            data_dir=args.data_dir,
            config=config
        )
        
        # Run complete pipeline
        results = system.run_complete_pipeline()
        
        # Return appropriate exit code
        execution_summary = results.get('execution_summary', {})
        if execution_summary.get('overall_success'):
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Pipeline interrupted by user")
        sys.exit(130)  # Interrupted
    except Exception as e:
        logging.getLogger(__name__).error(f"Pipeline failed with error: {str(e)}")
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
