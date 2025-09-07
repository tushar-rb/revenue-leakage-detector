#!/usr/bin/env python3
"""
Data Analyst Agent - The "Muscle" of the Revenue Leakage Detection System

This agent is responsible for:
1. Loading and joining data from multiple sources (billing, provisioning, usage, contracts)
2. Data cleaning and normalization
3. Feature engineering for leakage detection
4. Performance-optimized data processing using computational "muscle"

The agent uses pandas, numpy, and other data processing libraries to efficiently
handle large datasets and prepare them for analysis by the Audit Analyst Agent.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import sqlite3
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')

@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    total_records: int
    missing_values: Dict[str, int]
    duplicate_records: int
    data_inconsistencies: List[str]
    date_range: Tuple[str, str]
    recommendations: List[str]

class DataAnalystAgent:
    """
    Data Analyst Agent - Computational "Muscle" for data processing
    
    This agent handles all the heavy lifting of data preparation including:
    - Multi-table joins with optimized performance
    - Data cleaning and validation
    - Feature engineering
    - Data quality assessment
    - Preparation for downstream analysis
    """
    
    def __init__(self, data_dir: str = None, cache_enabled: bool = True):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / 'data'
        self.sample_dir = self.data_dir / 'sample'
        self.processed_dir = self.data_dir / 'processed'
        self.cache_enabled = cache_enabled
        
        # Ensure directories exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Data containers
        self.raw_data = {}
        self.processed_data = {}
        self.joined_data = None
        self.data_quality_report = None
        
        self.logger.info("Data Analyst Agent initialized - Ready to flex computational muscle!")
    
    def load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """Load all raw data sources with optimized performance"""
        self.logger.info("💪 Flexing muscle - Loading raw data sources...")
        
        data_sources = {
            'customers': 'customers.csv',
            'contracts': 'contracts.csv',
            'provisioning': 'provisioning_records.csv',
            'usage_logs': 'usage_logs.csv',
            'billing': 'billing_data.csv'
        }
        
        for source, filename in data_sources.items():
            file_path = self.sample_dir / filename
            
            if not file_path.exists():
                self.logger.warning(f"Data source not found: {file_path}")
                continue
            
            try:
                # Optimized loading with appropriate data types
                self.logger.info(f"  Loading {source} from {filename}...")
                
                if source == 'usage_logs':
                    # Large file - optimize loading
                    df = pd.read_csv(file_path, 
                                   parse_dates=['usage_date'],
                                   dtype={'usage_amount': 'float32'})
                elif source == 'billing':
                    df = pd.read_csv(file_path,
                                   parse_dates=['billing_date', 'due_date'],
                                   dtype={'total_amount': 'float32',
                                          'base_charge': 'float32',
                                          'overage_charge': 'float32'})
                elif source == 'contracts':
                    df = pd.read_csv(file_path,
                                   parse_dates=['start_date', 'end_date', 'promo_expiry_date'],
                                   dtype={'base_rate': 'float32',
                                          'contracted_rate': 'float32',
                                          'tier_multiplier': 'float32'})
                else:
                    df = pd.read_csv(file_path)
                
                self.raw_data[source] = df
                self.logger.info(f"    ✅ Loaded {len(df):,} records from {source}")
                
            except Exception as e:
                self.logger.error(f"Failed to load {source}: {str(e)}")
                continue
        
        total_records = sum(len(df) for df in self.raw_data.values())
        self.logger.info(f"🏋️ Total raw records loaded: {total_records:,}")
        
        return self.raw_data
    
    def clean_and_normalize_data(self) -> Dict[str, pd.DataFrame]:
        """Clean and normalize data with computational muscle"""
        self.logger.info("🧹 Cleaning and normalizing data...")
        
        for source, df in self.raw_data.items():
            self.logger.info(f"  Processing {source}...")
            
            # Make a copy to avoid modifying original
            cleaned_df = df.copy()
            
            # Remove duplicates
            original_count = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates()
            if len(cleaned_df) < original_count:
                self.logger.info(f"    Removed {original_count - len(cleaned_df)} duplicates")
            
            # Source-specific cleaning
            if source == 'billing':
                # Fix negative amounts (set to 0)
                negative_mask = cleaned_df['total_amount'] < 0
                if negative_mask.any():
                    cleaned_df.loc[negative_mask, 'total_amount'] = 0
                    self.logger.info(f"    Fixed {negative_mask.sum()} negative amounts")
                
                # Ensure billing status is consistent
                cleaned_df['status'] = cleaned_df['status'].fillna('UNKNOWN')
                
            elif source == 'usage_logs':
                # Remove records with negative usage
                positive_usage = cleaned_df['usage_amount'] >= 0
                if not positive_usage.all():
                    removed = (~positive_usage).sum()
                    cleaned_df = cleaned_df[positive_usage]
                    self.logger.info(f"    Removed {removed} records with negative usage")
            
            self.processed_data[source] = cleaned_df
            self.logger.info(f"    ✅ {source} cleaned: {len(cleaned_df):,} records")
        
        self.logger.info("🧹 Data cleaning complete!")
        return self.processed_data
    
    def perform_intelligent_joins(self) -> pd.DataFrame:
        """Perform optimized multi-table joins using computational muscle"""
        self.logger.info("🔗 Performing intelligent multi-table joins...")
        
        # Start with contracts as the base table (most comprehensive)
        base_df = self.processed_data['contracts'].copy()
        self.logger.info(f"  Base table (contracts): {len(base_df):,} records")
        
        # Join with customers
        if 'customers' in self.processed_data:
            customers_df = self.processed_data['customers']
            base_df = base_df.merge(
                customers_df[['customer_id', 'customer_name', 'tier', 'status', 'email']],
                on='customer_id',
                how='left',
                suffixes=('', '_customer')
            )
            self.logger.info(f"  After customer join: {len(base_df):,} records")
        
        # Join with billing data (aggregate first for performance)
        if 'billing' in self.processed_data:
            billing_df = self.processed_data['billing']
            
            # Aggregate billing by contract for better join performance
            billing_agg = billing_df.groupby('contract_id').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'billing_date': ['min', 'max'],
                'status': lambda x: x.mode().iloc[0] if not x.empty else 'UNKNOWN',
                'billing_error_type': lambda x: x.dropna().tolist(),
                'rate_error': 'any'
            }).reset_index()
            
            # Flatten column names
            billing_agg.columns = [
                'contract_id', 'total_billed', 'avg_bill_amount', 'bill_count',
                'first_bill_date', 'last_bill_date', 'billing_status',
                'error_types', 'has_rate_error'
            ]
            
            base_df = base_df.merge(billing_agg, on='contract_id', how='left')
            self.logger.info(f"  After billing join: {len(base_df):,} records")
        
        # Join with usage data (aggregate first for performance)
        if 'usage_logs' in self.processed_data:
            usage_df = self.processed_data['usage_logs']
            
            # Aggregate usage by contract
            usage_agg = usage_df.groupby('contract_id').agg({
                'usage_amount': ['sum', 'mean', 'max', 'count'],
                'usage_date': ['min', 'max']
            }).reset_index()
            
            # Flatten column names
            usage_agg.columns = [
                'contract_id', 'total_usage', 'avg_usage', 'max_daily_usage',
                'usage_days', 'first_usage_date', 'last_usage_date'
            ]
            
            base_df = base_df.merge(usage_agg, on='contract_id', how='left')
            self.logger.info(f"  After usage join: {len(base_df):,} records")
        
        # Fill missing values with appropriate defaults
        numeric_columns = base_df.select_dtypes(include=[np.number]).columns
        base_df[numeric_columns] = base_df[numeric_columns].fillna(0)
        
        # Create derived features for leakage detection
        base_df = self._create_derived_features(base_df)
        
        self.joined_data = base_df
        self.logger.info(f"🔗 Multi-table join complete! Final dataset: {len(base_df):,} records with {len(base_df.columns)} features")
        
        return base_df
    
    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features for leakage detection"""
        self.logger.info("⚙️ Engineering features for leakage detection...")
        
        # Revenue leakage indicators
        if 'total_billed' in df.columns and 'contracted_rate' in df.columns:
            # Expected vs actual revenue
            df['expected_monthly_revenue'] = df['contracted_rate'] * df['bill_count']
            df['revenue_variance'] = df['expected_monthly_revenue'] - df['total_billed']
            df['revenue_variance_pct'] = np.where(
                df['expected_monthly_revenue'] > 0,
                (df['revenue_variance'] / df['expected_monthly_revenue']) * 100,
                0
            )
        
        # Usage-based leakage indicators
        if 'total_usage' in df.columns and 'included_usage' in df.columns:
            df['expected_overage_usage'] = np.maximum(0, df['total_usage'] - df['included_usage'])
            df['expected_overage_revenue'] = df['expected_overage_usage'] * df['overage_rate']
        
        # Risk scoring
        risk_factors = []
        
        if 'revenue_variance_pct' in df.columns:
            risk_factors.append((df['revenue_variance_pct'].abs() > 10).astype(int))
        
        if 'has_rate_error' in df.columns:
            risk_factors.append(df['has_rate_error'].astype(int))
        
        if risk_factors:
            df['leakage_risk_score'] = sum(risk_factors)
        else:
            df['leakage_risk_score'] = 0
        
        self.logger.info("⚙️ Feature engineering complete!")
        
        return df
    
    def save_processed_data(self) -> bool:
        """Save processed and joined data for downstream agents"""
        try:
            if self.joined_data is not None:
                output_file = self.processed_dir / 'joined_data.csv'
                self.joined_data.to_csv(output_file, index=False)
                self.logger.info(f"💾 Saved joined data to {output_file}")
                
                # Save to SQLite for efficient querying
                db_file = self.processed_dir / 'revenue_data.db'
                with sqlite3.connect(db_file) as conn:
                    self.joined_data.to_sql('revenue_analysis', conn, if_exists='replace', index=False)
                    self.logger.info(f"💾 Saved to SQLite database: {db_file}")
                
                return True
            else:
                self.logger.error("No joined data to save")
                return False
        
        except Exception as e:
            self.logger.error(f"Failed to save processed data: {str(e)}")
            return False
    
    def get_processing_summary(self) -> Dict:
        """Get summary of data processing results"""
        summary = {
            'agent_type': 'Data Analyst Agent (Muscle)',
            'processing_timestamp': datetime.now().isoformat(),
            'raw_data_sources': len(self.raw_data),
            'processed_datasets': len(self.processed_data),
            'final_joined_records': len(self.joined_data) if self.joined_data is not None else 0,
            'final_feature_count': len(self.joined_data.columns) if self.joined_data is not None else 0,
            'ready_for_audit_agent': self.joined_data is not None
        }
        
        return summary
    
    def run_full_analysis(self) -> Tuple[pd.DataFrame, Dict]:
        """Run the complete data analysis pipeline"""
        self.logger.info("🚀 Starting Data Analyst Agent - Full Analysis Pipeline")
        
        try:
            # Step 1: Load raw data
            self.load_raw_data()
            
            # Step 2: Clean and normalize
            self.clean_and_normalize_data()
            
            # Step 3: Perform joins and feature engineering
            joined_data = self.perform_intelligent_joins()
            
            # Step 4: Save processed data
            self.save_processed_data()
            
            # Step 5: Generate summary
            summary = self.get_processing_summary()
            
            self.logger.info("💪 Data Analyst Agent processing complete!")
            self.logger.info(f"📊 Final dataset ready for Audit Analyst Agent: {len(joined_data):,} records")
            
            return joined_data, summary
            
        except Exception as e:
            self.logger.error(f"Data analysis pipeline failed: {str(e)}")
            raise

# Agent initialization function
def create_data_analyst_agent(data_dir: str = None) -> DataAnalystAgent:
    """Factory function to create and configure Data Analyst Agent"""
    return DataAnalystAgent(data_dir=data_dir)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run agent
    agent = create_data_analyst_agent()
    joined_data, summary = agent.run_full_analysis()
    
    print("\n" + "="*60)
    print("DATA ANALYST AGENT - PROCESSING SUMMARY")
    print("="*60)
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("="*60)
