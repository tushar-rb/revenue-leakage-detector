#!/usr/bin/env python3
"""
Audit Analyst Agent - The "Muscle + Brain" of Revenue Leakage Detection

This agent combines:
MUSCLE (Mathematical Analysis):
- Statistical analysis for discrepancy detection
- Mathematical models for pattern recognition
- Quantitative risk assessment
- Performance-optimized computations

BRAIN (AI Context Understanding):
- Contextual analysis of business patterns
- Intelligent interpretation of anomalies
- Learning from historical patterns
- Natural language reasoning about findings

The agent takes processed data from the Data Analyst Agent and performs
sophisticated analysis to detect various types of revenue leakage.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional, NamedTuple
import sqlite3
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import warnings
import json

warnings.filterwarnings('ignore')

@dataclass
class LeakageDetection:
    """Individual revenue leakage detection result"""
    detection_id: str
    customer_id: str
    contract_id: str
    leakage_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    estimated_loss: float
    description: str
    mathematical_evidence: Dict
    contextual_analysis: str
    recommended_action: str
    detection_timestamp: datetime

class AuditAnalystAgent:
    """
    Audit Analyst Agent - Combining Mathematical Muscle with AI Brain
    
    This agent performs sophisticated revenue leakage detection using:
    1. MUSCLE: Statistical analysis, pattern recognition, mathematical models
    2. BRAIN: Contextual understanding, intelligent interpretation, learning
    """
    
    def __init__(self, data_dir: str = None, confidence_threshold: float = 0.7):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / 'data'
        self.processed_dir = self.data_dir / 'processed'
        self.confidence_threshold = confidence_threshold
        
        # Analysis components
        self.data = None
        self.detections = []
        self.analysis_summary = {}
        
        # ML models for anomaly detection (MUSCLE)
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        # Business rules and thresholds (BRAIN)
        self.leakage_rules = self._initialize_business_rules()
        
        self.logger.info("Audit Analyst Agent initialized - Muscle + Brain ready for analysis!")
    
    def _initialize_business_rules(self) -> Dict:
        """Initialize business rules for intelligent analysis (BRAIN)"""
        return {
            'missing_charges': {
                'threshold': 0.0,
                'severity_mapping': {
                    (0, 100): 'LOW',
                    (100, 1000): 'MEDIUM',
                    (1000, 5000): 'HIGH',
                    (5000, float('inf')): 'CRITICAL'
                }
            },
            'incorrect_rates': {
                'variance_threshold': 0.05,  # 5% variance allowed
                'severity_mapping': {
                    (0, 50): 'LOW',
                    (50, 500): 'MEDIUM',
                    (500, 2000): 'HIGH',
                    (2000, float('inf')): 'CRITICAL'
                }
            },
            'usage_mismatches': {
                'variance_threshold': 0.15,  # 15% variance allowed
                'severity_mapping': {
                    (0, 25): 'LOW',
                    (25, 200): 'MEDIUM',
                    (200, 1000): 'HIGH',
                    (1000, float('inf')): 'CRITICAL'
                }
            },
            'duplicate_entries': {
                'threshold': 1,
                'severity_mapping': {
                    (0, 50): 'LOW',
                    (50, 200): 'MEDIUM',
                    (200, 1000): 'HIGH',
                    (1000, float('inf')): 'CRITICAL'
                }
            }
        }
    
    def load_processed_data(self) -> pd.DataFrame:
        """Load processed data from Data Analyst Agent"""
        self.logger.info("🧠 Brain activating - Loading processed data...")
        
        # Try loading from CSV first
        csv_file = self.processed_dir / 'joined_data.csv'
        if csv_file.exists():
            self.data = pd.read_csv(csv_file)
            self.logger.info(f"📊 Loaded {len(self.data):,} records from {csv_file}")
        else:
            # Try SQLite database
            db_file = self.processed_dir / 'revenue_data.db'
            if db_file.exists():
                with sqlite3.connect(db_file) as conn:
                    self.data = pd.read_sql_query("SELECT * FROM revenue_analysis", conn)
                self.logger.info(f"📊 Loaded {len(self.data):,} records from database")
            else:
                raise FileNotFoundError("No processed data found from Data Analyst Agent")
        
        return self.data
    
    def detect_missing_charges(self) -> List[LeakageDetection]:
        """MUSCLE + BRAIN: Detect missing charges using mathematical and contextual analysis"""
        self.logger.info("🔍 MUSCLE + BRAIN: Analyzing missing charges...")
        
        detections = []
        
        # MUSCLE: Mathematical analysis
        missing_charge_candidates = self.data[
            (self.data['total_billed'] == 0) | 
            (self.data['total_billed'].isna()) |
            (self.data['bill_count'] == 0)
        ].copy()
        
        self.logger.info(f"  MUSCLE: Found {len(missing_charge_candidates)} mathematical candidates")
        
        for _, record in missing_charge_candidates.iterrows():
            # Calculate expected revenue (MUSCLE)
            expected_revenue = record.get('contracted_rate', 0) * max(1, record.get('bill_count', 0))
            actual_revenue = record.get('total_billed', 0)
            estimated_loss = expected_revenue - actual_revenue
            
            # BRAIN: Contextual analysis
            context_factors = []
            
            # Check service status
            if record.get('status') == 'Active':
                context_factors.append("Service is active but not generating revenue")
            
            # Check usage patterns
            if record.get('total_usage', 0) > 0:
                context_factors.append(f"Customer has {record.get('total_usage', 0):.2f} units of usage")
            
            # Check contract validity
            if pd.notna(record.get('start_date')) and pd.notna(record.get('end_date')):
                context_factors.append("Valid contract period exists")
            
            # BRAIN: Determine severity and confidence
            severity = self._calculate_severity('missing_charges', estimated_loss)
            confidence = self._calculate_confidence_missing_charges(record, context_factors)
            
            # BRAIN: Generate contextual description
            description = self._generate_missing_charge_description(record, context_factors, estimated_loss)
            
            if confidence >= self.confidence_threshold:
                detection = LeakageDetection(
                    detection_id=f"MISS_{record['contract_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    customer_id=record['customer_id'],
                    contract_id=record['contract_id'],
                    leakage_type='MISSING_CHARGES',
                    severity=severity,
                    confidence=confidence,
                    estimated_loss=estimated_loss,
                    description=description,
                    mathematical_evidence={
                        'expected_revenue': expected_revenue,
                        'actual_revenue': actual_revenue,
                        'bill_count': record.get('bill_count', 0),
                        'contracted_rate': record.get('contracted_rate', 0)
                    },
                    contextual_analysis=' | '.join(context_factors),
                    recommended_action=self._recommend_action_missing_charges(record, severity),
                    detection_timestamp=datetime.now()
                )
                detections.append(detection)
        
        self.logger.info(f"  🎯 Detected {len(detections)} high-confidence missing charge cases")
        return detections
    
    def detect_incorrect_rates(self) -> List[LeakageDetection]:
        """MUSCLE + BRAIN: Detect incorrect billing rates"""
        self.logger.info("🔍 MUSCLE + BRAIN: Analyzing incorrect rates...")
        
        detections = []
        
        # MUSCLE: Mathematical analysis of rate discrepancies
        rate_analysis = self.data.copy()
        
        # Calculate expected vs actual rates
        rate_analysis['expected_rate'] = rate_analysis['base_rate'] * rate_analysis['tier_multiplier']
        rate_analysis['rate_variance'] = abs(rate_analysis['expected_rate'] - rate_analysis.get('avg_bill_amount', 0))
        rate_analysis['rate_variance_pct'] = np.where(
            rate_analysis['expected_rate'] > 0,
            (rate_analysis['rate_variance'] / rate_analysis['expected_rate']) * 100,
            0
        )
        
        # Filter significant rate variances
        incorrect_rate_candidates = rate_analysis[
            (rate_analysis['rate_variance_pct'] > self.leakage_rules['incorrect_rates']['variance_threshold'] * 100) &
            (rate_analysis['rate_variance'] > 10)  # Minimum variance threshold
        ].copy()
        
        self.logger.info(f"  MUSCLE: Found {len(incorrect_rate_candidates)} rate variance candidates")
        
        for _, record in incorrect_rate_candidates.iterrows():
            # MUSCLE: Calculate financial impact
            estimated_loss = record['rate_variance'] * record.get('bill_count', 1)
            
            # BRAIN: Contextual analysis
            context_factors = []
            
            # Check promotional rates
            if record.get('is_promotional'):
                context_factors.append("Contract has promotional rates")
                if pd.notna(record.get('promo_expiry_date')):
                    context_factors.append(f"Promotion expired: {record.get('promo_expiry_date')}")
            
            # Check customer tier
            if record.get('tier'):
                context_factors.append(f"Customer tier: {record.get('tier')}")
            
            # Check rate error flag
            if record.get('has_rate_error'):
                context_factors.append("System flagged rate errors detected")
            
            # BRAIN: Calculate confidence and severity
            confidence = self._calculate_confidence_incorrect_rates(record, context_factors)
            severity = self._calculate_severity('incorrect_rates', estimated_loss)
            
            # BRAIN: Generate description
            description = self._generate_rate_error_description(record, estimated_loss)
            
            if confidence >= self.confidence_threshold:
                detection = LeakageDetection(
                    detection_id=f"RATE_{record['contract_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    customer_id=record['customer_id'],
                    contract_id=record['contract_id'],
                    leakage_type='INCORRECT_RATES',
                    severity=severity,
                    confidence=confidence,
                    estimated_loss=estimated_loss,
                    description=description,
                    mathematical_evidence={
                        'expected_rate': record['expected_rate'],
                        'actual_avg_rate': record.get('avg_bill_amount', 0),
                        'variance_percentage': record['rate_variance_pct'],
                        'variance_amount': record['rate_variance']
                    },
                    contextual_analysis=' | '.join(context_factors),
                    recommended_action=self._recommend_action_incorrect_rates(record, severity),
                    detection_timestamp=datetime.now()
                )
                detections.append(detection)
        
        self.logger.info(f"  🎯 Detected {len(detections)} incorrect rate cases")
        return detections
    
    def detect_usage_mismatches(self) -> List[LeakageDetection]:
        """MUSCLE + BRAIN: Detect usage vs billing mismatches"""
        self.logger.info("🔍 MUSCLE + BRAIN: Analyzing usage mismatches...")
        
        detections = []
        
        # MUSCLE: Statistical analysis of usage patterns
        usage_analysis = self.data[self.data['usage_based'] == True].copy()
        
        if len(usage_analysis) == 0:
            self.logger.info("  No usage-based services found")
            return detections
        
        # Calculate expected overage revenue
        usage_analysis['actual_overage_usage'] = np.maximum(0, usage_analysis['total_usage'] - usage_analysis['included_usage'])
        usage_analysis['expected_overage_revenue'] = usage_analysis['actual_overage_usage'] * usage_analysis['overage_rate']
        
        # Compare with billed overage
        usage_analysis['overage_variance'] = usage_analysis['expected_overage_revenue'] - usage_analysis.get('overage_charge', 0)
        usage_analysis['usage_variance_pct'] = np.where(
            usage_analysis['expected_overage_revenue'] > 0,
            abs(usage_analysis['overage_variance'] / usage_analysis['expected_overage_revenue']) * 100,
            0
        )
        
        # Filter significant usage mismatches
        mismatch_candidates = usage_analysis[
            (usage_analysis['usage_variance_pct'] > self.leakage_rules['usage_mismatches']['variance_threshold'] * 100) &
            (abs(usage_analysis['overage_variance']) > 5)
        ].copy()
        
        self.logger.info(f"  MUSCLE: Found {len(mismatch_candidates)} usage mismatch candidates")
        
        for _, record in mismatch_candidates.iterrows():
            # MUSCLE: Calculate impact
            estimated_loss = abs(record['overage_variance'])
            
            # BRAIN: Contextual analysis
            context_factors = []
            
            # Usage pattern analysis
            avg_daily_usage = record.get('total_usage', 0) / max(1, record.get('usage_days', 1))
            context_factors.append(f"Average daily usage: {avg_daily_usage:.2f} {record.get('usage_unit', 'units')}")
            
            # Service type context
            context_factors.append(f"Service type: {record.get('service_type', 'Unknown')}")
            
            # Overage analysis
            if record['actual_overage_usage'] > 0:
                context_factors.append(f"Overage usage: {record['actual_overage_usage']:.2f} units")
            
            # BRAIN: Determine confidence and severity
            confidence = self._calculate_confidence_usage_mismatch(record, context_factors)
            severity = self._calculate_severity('usage_mismatches', estimated_loss)
            
            # BRAIN: Generate description
            description = self._generate_usage_mismatch_description(record, estimated_loss)
            
            if confidence >= self.confidence_threshold:
                detection = LeakageDetection(
                    detection_id=f"USAGE_{record['contract_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    customer_id=record['customer_id'],
                    contract_id=record['contract_id'],
                    leakage_type='USAGE_MISMATCHES',
                    severity=severity,
                    confidence=confidence,
                    estimated_loss=estimated_loss,
                    description=description,
                    mathematical_evidence={
                        'total_usage': record.get('total_usage', 0),
                        'included_usage': record.get('included_usage', 0),
                        'expected_overage_revenue': record['expected_overage_revenue'],
                        'actual_overage_charge': record.get('overage_charge', 0),
                        'variance_percentage': record['usage_variance_pct']
                    },
                    contextual_analysis=' | '.join(context_factors),
                    recommended_action=self._recommend_action_usage_mismatch(record, severity),
                    detection_timestamp=datetime.now()
                )
                detections.append(detection)
        
        self.logger.info(f"  🎯 Detected {len(detections)} usage mismatch cases")
        return detections
    
    def detect_duplicate_entries(self) -> List[LeakageDetection]:
        """MUSCLE + BRAIN: Detect duplicate billing entries using advanced analysis"""
        self.logger.info("🔍 MUSCLE + BRAIN: Analyzing duplicate entries...")
        
        detections = []
        
        # MUSCLE: Statistical duplicate detection
        if 'error_types' not in self.data.columns:
            self.logger.info("  No error type information available for duplicate detection")
            return detections
        
        # Find records with duplicate error flags
        duplicate_candidates = self.data[
            self.data['error_types'].apply(lambda x: 'DUPLICATE_ENTRY' in str(x) if pd.notna(x) else False)
        ].copy()
        
        self.logger.info(f"  MUSCLE: Found {len(duplicate_candidates)} duplicate entry candidates")
        
        for _, record in duplicate_candidates.iterrows():
            # MUSCLE: Calculate estimated impact
            estimated_loss = record.get('total_billed', 0)  # Full amount if duplicate
            
            # BRAIN: Contextual analysis
            context_factors = []
            context_factors.append(f"Billing amount: ${estimated_loss:.2f}")
            context_factors.append(f"Service: {record.get('service_type', 'Unknown')}")
            
            if record.get('bill_count', 0) > 1:
                context_factors.append(f"Multiple bills detected: {record.get('bill_count', 0)}")
            
            # BRAIN: High confidence for flagged duplicates
            confidence = 0.9
            severity = self._calculate_severity('duplicate_entries', estimated_loss)
            
            # BRAIN: Generate description
            description = f"Duplicate billing entry detected for {record.get('service_type', 'service')} " + \
                         f"service with potential overcharge of ${estimated_loss:.2f}"
            
            detection = LeakageDetection(
                detection_id=f"DUP_{record['contract_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                customer_id=record['customer_id'],
                contract_id=record['contract_id'],
                leakage_type='DUPLICATE_ENTRIES',
                severity=severity,
                confidence=confidence,
                estimated_loss=estimated_loss,
                description=description,
                mathematical_evidence={
                    'duplicated_amount': estimated_loss,
                    'bill_count': record.get('bill_count', 0),
                    'error_flags': str(record.get('error_types', []))
                },
                contextual_analysis=' | '.join(context_factors),
                recommended_action=self._recommend_action_duplicate_entries(record, severity),
                detection_timestamp=datetime.now()
            )
            detections.append(detection)
        
        self.logger.info(f"  🎯 Detected {len(detections)} duplicate entry cases")
        return detections
    
    def perform_anomaly_detection(self) -> List[LeakageDetection]:
        """MUSCLE: Advanced statistical anomaly detection using machine learning"""
        self.logger.info("💪 MUSCLE: Performing ML-based anomaly detection...")
        
        detections = []
        
        # Prepare features for anomaly detection
        feature_columns = [
            'contracted_rate', 'total_billed', 'avg_bill_amount', 'bill_count',
            'revenue_variance_pct', 'leakage_risk_score'
        ]
        
        # Filter valid numeric data
        ml_data = self.data[feature_columns].copy()
        ml_data = ml_data.fillna(0)
        
        if len(ml_data) < 10:
            self.logger.warning("Insufficient data for ML anomaly detection")
            return detections
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(ml_data)
        
        # Detect anomalies
        anomaly_predictions = self.isolation_forest.fit_predict(features_scaled)
        anomaly_scores = self.isolation_forest.decision_function(features_scaled)
        
        # Add results to dataframe
        anomaly_df = self.data.copy()
        anomaly_df['is_anomaly'] = anomaly_predictions == -1
        anomaly_df['anomaly_score'] = anomaly_scores
        
        # Filter significant anomalies
        significant_anomalies = anomaly_df[
            (anomaly_df['is_anomaly']) & 
            (anomaly_df['anomaly_score'] < -0.1)  # More stringent threshold
        ]
        
        self.logger.info(f"  MUSCLE: Found {len(significant_anomalies)} statistical anomalies")
        
        for _, record in significant_anomalies.iterrows():
            # Calculate potential loss based on revenue variance
            estimated_loss = abs(record.get('revenue_variance', 0))
            
            if estimated_loss < 10:  # Skip minor anomalies
                continue
            
            # BRAIN: Contextual interpretation of anomaly
            context_factors = []
            context_factors.append(f"Anomaly score: {record['anomaly_score']:.3f}")
            context_factors.append(f"Risk score: {record.get('leakage_risk_score', 0)}")
            
            confidence = min(0.8, abs(record['anomaly_score']) * 2)  # Convert to confidence
            severity = self._calculate_severity('missing_charges', estimated_loss)
            
            description = f"Statistical anomaly detected in billing pattern with score {record['anomaly_score']:.3f}. " + \
                         f"Potential revenue impact: ${estimated_loss:.2f}"
            
            detection = LeakageDetection(
                detection_id=f"ANOM_{record['contract_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                customer_id=record['customer_id'],
                contract_id=record['contract_id'],
                leakage_type='STATISTICAL_ANOMALY',
                severity=severity,
                confidence=confidence,
                estimated_loss=estimated_loss,
                description=description,
                mathematical_evidence={
                    'anomaly_score': record['anomaly_score'],
                    'features_analyzed': feature_columns,
                    'revenue_variance': record.get('revenue_variance', 0)
                },
                contextual_analysis=' | '.join(context_factors),
                recommended_action="Investigate anomalous billing pattern and verify calculations",
                detection_timestamp=datetime.now()
            )
            detections.append(detection)
        
        self.logger.info(f"  🎯 Detected {len(detections)} significant anomalies")
        return detections
    
    # Helper methods for BRAIN functionality
    def _calculate_severity(self, leakage_type: str, estimated_loss: float) -> str:
        """BRAIN: Calculate severity based on business rules"""
        severity_mapping = self.leakage_rules[leakage_type]['severity_mapping']
        
        for (min_val, max_val), severity in severity_mapping.items():
            if min_val <= estimated_loss < max_val:
                return severity
        
        return 'LOW'  # Default
    
    def _calculate_confidence_missing_charges(self, record: pd.Series, context_factors: List[str]) -> float:
        """BRAIN: Calculate confidence for missing charges detection"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on context
        if record.get('status') == 'Active':
            confidence += 0.2
        
        if record.get('total_usage', 0) > 0:
            confidence += 0.2
        
        if record.get('bill_count', 0) == 0:
            confidence += 0.3
        
        return min(1.0, confidence)
    
    def _calculate_confidence_incorrect_rates(self, record: pd.Series, context_factors: List[str]) -> float:
        """BRAIN: Calculate confidence for incorrect rates"""
        confidence = 0.6  # Base confidence
        
        # Higher confidence if system flagged errors
        if record.get('has_rate_error'):
            confidence += 0.3
        
        # Higher confidence for larger variances
        if record.get('rate_variance_pct', 0) > 20:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _calculate_confidence_usage_mismatch(self, record: pd.Series, context_factors: List[str]) -> float:
        """BRAIN: Calculate confidence for usage mismatches"""
        confidence = 0.6  # Base confidence
        
        # Higher confidence for larger variances
        if record.get('usage_variance_pct', 0) > 50:
            confidence += 0.2
        
        # Higher confidence if significant usage exists
        if record.get('total_usage', 0) > record.get('included_usage', 0):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_missing_charge_description(self, record: pd.Series, context_factors: List[str], estimated_loss: float) -> str:
        """BRAIN: Generate contextual description for missing charges"""
        service_type = record.get('service_type', 'service')
        customer_name = record.get('customer_name', record.get('customer_id', 'Unknown'))
        
        return f"Missing charges detected for {customer_name}'s {service_type} service. " + \
               f"Expected revenue: ${record.get('contracted_rate', 0):.2f}, " + \
               f"Actual billed: ${record.get('total_billed', 0):.2f}. " + \
               f"Potential loss: ${estimated_loss:.2f}"
    
    def _generate_rate_error_description(self, record: pd.Series, estimated_loss: float) -> str:
        """BRAIN: Generate description for rate errors"""
        return f"Incorrect billing rate detected. Expected: ${record.get('expected_rate', 0):.2f}, " + \
               f"Applied: ${record.get('avg_bill_amount', 0):.2f}. " + \
               f"Variance: {record.get('rate_variance_pct', 0):.1f}%. " + \
               f"Estimated impact: ${estimated_loss:.2f}"
    
    def _generate_usage_mismatch_description(self, record: pd.Series, estimated_loss: float) -> str:
        """BRAIN: Generate description for usage mismatches"""
        return f"Usage billing mismatch detected. Total usage: {record.get('total_usage', 0):.2f}, " + \
               f"Expected overage revenue: ${record.get('expected_overage_revenue', 0):.2f}, " + \
               f"Actual overage charge: ${record.get('overage_charge', 0):.2f}. " + \
               f"Variance: ${estimated_loss:.2f}"
    
    def _recommend_action_missing_charges(self, record: pd.Series, severity: str) -> str:
        """BRAIN: Recommend actions for missing charges"""
        if severity == 'CRITICAL':
            return "URGENT: Immediately investigate and generate missing bills. Contact customer if necessary."
        elif severity == 'HIGH':
            return "Generate missing charges and apply to next billing cycle. Review billing system configuration."
        else:
            return "Review and apply missing charges. Monitor for recurring issues."
    
    def _recommend_action_incorrect_rates(self, record: pd.Series, severity: str) -> str:
        """BRAIN: Recommend actions for rate errors"""
        if record.get('has_rate_error'):
            return "System-detected rate error: Review and correct rate configuration immediately."
        else:
            return "Manual review required: Verify rate calculation and apply corrections if confirmed."
    
    def _recommend_action_usage_mismatch(self, record: pd.Series, severity: str) -> str:
        """BRAIN: Recommend actions for usage mismatches"""
        return "Review usage metering system and billing calculation. Verify overage charges are correctly applied."
    
    def _recommend_action_duplicate_entries(self, record: pd.Series, severity: str) -> str:
        """BRAIN: Recommend actions for duplicates"""
        return "Remove duplicate entry and issue credit to customer if payment was processed."
    
    def run_full_audit(self) -> Tuple[List[LeakageDetection], Dict]:
        """Run comprehensive audit analysis combining all detection methods"""
        self.logger.info("🚀 Starting Audit Analyst Agent - Full Analysis Pipeline")
        
        try:
            # Step 1: Load processed data
            self.load_processed_data()
            
            # Step 2: Run all detection methods
            all_detections = []
            
            # Missing charges detection
            missing_detections = self.detect_missing_charges()
            all_detections.extend(missing_detections)
            
            # Incorrect rates detection
            rate_detections = self.detect_incorrect_rates()
            all_detections.extend(rate_detections)
            
            # Usage mismatches detection
            usage_detections = self.detect_usage_mismatches()
            all_detections.extend(usage_detections)
            
            # Duplicate entries detection
            duplicate_detections = self.detect_duplicate_entries()
            all_detections.extend(duplicate_detections)
            
            # Statistical anomaly detection
            anomaly_detections = self.perform_anomaly_detection()
            all_detections.extend(anomaly_detections)
            
            self.detections = all_detections
            
            # Step 3: Generate analysis summary
            summary = self._generate_analysis_summary()
            
            # Step 4: Save results
            self._save_detection_results()
            
            self.logger.info("🧠💪 Audit Analyst Agent analysis complete!")
            self.logger.info(f"📊 Total detections: {len(all_detections)}")
            
            return all_detections, summary
            
        except Exception as e:
            self.logger.error(f"Audit analysis failed: {str(e)}")
            raise
    
    def _generate_analysis_summary(self) -> Dict:
        """Generate comprehensive analysis summary"""
        total_detections = len(self.detections)
        total_estimated_loss = sum(d.estimated_loss for d in self.detections)
        
        # Group by type and severity
        by_type = {}
        by_severity = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        
        for detection in self.detections:
            # By type
            if detection.leakage_type not in by_type:
                by_type[detection.leakage_type] = {'count': 0, 'loss': 0.0}
            by_type[detection.leakage_type]['count'] += 1
            by_type[detection.leakage_type]['loss'] += detection.estimated_loss
            
            # By severity
            by_severity[detection.severity] += 1
        
        summary = {
            'agent_type': 'Audit Analyst Agent (Muscle + Brain)',
            'analysis_timestamp': datetime.now().isoformat(),
            'total_records_analyzed': len(self.data) if self.data is not None else 0,
            'total_detections': total_detections,
            'total_estimated_loss': round(total_estimated_loss, 2),
            'detections_by_type': by_type,
            'detections_by_severity': by_severity,
            'high_priority_count': by_severity['HIGH'] + by_severity['CRITICAL'],
            'average_confidence': round(np.mean([d.confidence for d in self.detections]), 3) if self.detections else 0,
            'ready_for_reporting_agent': len(self.detections) > 0
        }
        
        return summary
    
    def _save_detection_results(self):
        """Save detection results for Reporting Agent"""
        if not self.detections:
            return
        
        # Convert detections to DataFrame
        detection_records = []
        for detection in self.detections:
            record = {
                'detection_id': detection.detection_id,
                'customer_id': detection.customer_id,
                'contract_id': detection.contract_id,
                'leakage_type': detection.leakage_type,
                'severity': detection.severity,
                'confidence': detection.confidence,
                'estimated_loss': detection.estimated_loss,
                'description': detection.description,
                'mathematical_evidence': json.dumps(detection.mathematical_evidence),
                'contextual_analysis': detection.contextual_analysis,
                'recommended_action': detection.recommended_action,
                'detection_timestamp': detection.detection_timestamp.isoformat()
            }
            detection_records.append(record)
        
        # Save to CSV
        detections_df = pd.DataFrame(detection_records)
        output_file = self.processed_dir / 'audit_detections.csv'
        detections_df.to_csv(output_file, index=False)
        self.logger.info(f"💾 Saved {len(detections_df)} detections to {output_file}")
        
        # Save to database
        db_file = self.processed_dir / 'revenue_data.db'
        with sqlite3.connect(db_file) as conn:
            detections_df.to_sql('audit_detections', conn, if_exists='replace', index=False)
            self.logger.info(f"💾 Saved detections to database: {db_file}")

# Agent initialization function
def create_audit_analyst_agent(data_dir: str = None, confidence_threshold: float = 0.7) -> AuditAnalystAgent:
    """Factory function to create Audit Analyst Agent"""
    return AuditAnalystAgent(data_dir=data_dir, confidence_threshold=confidence_threshold)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run agent
    agent = create_audit_analyst_agent()
    detections, summary = agent.run_full_audit()
    
    print("\n" + "="*60)
    print("AUDIT ANALYST AGENT - ANALYSIS SUMMARY")
    print("="*60)
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"{key.replace('_', ' ').title()}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    print("="*60)
