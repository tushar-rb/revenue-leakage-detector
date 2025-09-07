#!/usr/bin/env python3
"""
Sample Data Generator for Revenue Leakage Detection System

This script generates realistic sample data for testing the revenue leakage detection system.
It creates four main datasets:
1. Billing Data - Customer billing records
2. Service Provisioning Records - Service activation/deactivation records
3. Usage Logs - Actual service usage data
4. Contract Data - Customer contracts with pricing information

The script intentionally introduces various types of revenue leakage scenarios for testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
import json
from pathlib import Path

# Set random seeds for reproducible results
np.random.seed(42)
random.seed(42)

class SampleDataGenerator:
    def __init__(self, num_customers=1000, num_months=12):
        self.num_customers = num_customers
        self.num_months = num_months
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        
        # Service types and their characteristics
        self.service_types = {
            'Internet': {'base_rate': 50.0, 'usage_based': True, 'unit': 'GB'},
            'Phone': {'base_rate': 25.0, 'usage_based': True, 'unit': 'minutes'},
            'TV': {'base_rate': 80.0, 'usage_based': False, 'unit': 'subscription'},
            'Cloud_Storage': {'base_rate': 10.0, 'usage_based': True, 'unit': 'GB'},
            'VPN': {'base_rate': 15.0, 'usage_based': False, 'unit': 'subscription'},
            'Email': {'base_rate': 5.0, 'usage_based': True, 'unit': 'mailboxes'},
        }
        
        # Customer tiers with different rates
        self.customer_tiers = {
            'Basic': 1.0,
            'Premium': 1.2,
            'Enterprise': 1.5,
            'VIP': 1.8
        }
        
        self.output_dir = Path(__file__).parent.parent / 'data' / 'sample'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_customers(self):
        """Generate customer master data"""
        customers = []
        
        for i in range(self.num_customers):
            customer = {
                'customer_id': f'CUST{i+1:06d}',
                'customer_name': f'Customer {i+1}',
                'tier': random.choice(list(self.customer_tiers.keys())),
                'signup_date': self.start_date + timedelta(days=random.randint(0, 30)),
                'status': random.choice(['Active', 'Active', 'Active', 'Active', 'Suspended', 'Cancelled']),
                'email': f'customer{i+1}@example.com',
                'phone': f'+1-555-{random.randint(1000000, 9999999)}',
                'address': f'{random.randint(100, 9999)} Main St, City {i+1}',
            }
            customers.append(customer)
        
        return pd.DataFrame(customers)
    
    def generate_contracts(self, customers_df):
        """Generate contract data with pricing information"""
        contracts = []
        
        for _, customer in customers_df.iterrows():
            # Each customer has 1-3 services
            num_services = random.randint(1, 3)
            selected_services = random.sample(list(self.service_types.keys()), num_services)
            
            for service in selected_services:
                # Some contracts have promotional rates (intentional source of leakage)
                is_promotional = random.random() < 0.3
                promo_expiry = None
                
                if is_promotional:
                    promo_discount = random.uniform(0.2, 0.5)  # 20-50% discount
                    promo_expiry = customer['signup_date'] + timedelta(days=random.randint(90, 365))
                else:
                    promo_discount = 0.0
                
                base_rate = self.service_types[service]['base_rate']
                tier_multiplier = self.customer_tiers[customer['tier']]
                
                contract = {
                    'contract_id': f'CNT{uuid.uuid4().hex[:8].upper()}',
                    'customer_id': customer['customer_id'],
                    'service_type': service,
                    'start_date': customer['signup_date'],
                    'end_date': customer['signup_date'] + timedelta(days=365 * 2),  # 2-year contracts
                    'base_rate': base_rate,
                    'tier_multiplier': tier_multiplier,
                    'contracted_rate': base_rate * tier_multiplier * (1 - promo_discount),
                    'is_promotional': is_promotional,
                    'promo_expiry_date': promo_expiry,
                    'usage_based': self.service_types[service]['usage_based'],
                    'usage_unit': self.service_types[service]['unit'],
                    'included_usage': random.randint(100, 1000) if self.service_types[service]['usage_based'] else 0,
                    'overage_rate': round(base_rate * 0.1, 2) if self.service_types[service]['usage_based'] else 0,
                }
                contracts.append(contract)
        
        return pd.DataFrame(contracts)
    
    def generate_provisioning_records(self, contracts_df):
        """Generate service provisioning records"""
        provisioning_records = []
        
        for _, contract in contracts_df.iterrows():
            # Service activation record
            activation_record = {
                'provisioning_id': f'PROV{uuid.uuid4().hex[:8].upper()}',
                'customer_id': contract['customer_id'],
                'contract_id': contract['contract_id'],
                'service_type': contract['service_type'],
                'action': 'ACTIVATE',
                'action_date': contract['start_date'],
                'status': 'COMPLETED',
                'requested_by': 'SYSTEM',
                'notes': f'{contract["service_type"]} service activated for customer',
            }
            provisioning_records.append(activation_record)
            
            # Some services have modifications (upgrades/downgrades)
            if random.random() < 0.2:  # 20% chance of service modification
                modification_date = contract['start_date'] + timedelta(days=random.randint(30, 300))
                modification_record = {
                    'provisioning_id': f'PROV{uuid.uuid4().hex[:8].upper()}',
                    'customer_id': contract['customer_id'],
                    'contract_id': contract['contract_id'],
                    'service_type': contract['service_type'],
                    'action': random.choice(['UPGRADE', 'DOWNGRADE', 'MODIFY']),
                    'action_date': modification_date,
                    'status': 'COMPLETED',
                    'requested_by': 'CUSTOMER',
                    'notes': f'{contract["service_type"]} service modified',
                }
                provisioning_records.append(modification_record)
            
            # Some services are deactivated (creates potential for missing charges)
            if random.random() < 0.1:  # 10% chance of deactivation
                deactivation_date = contract['start_date'] + timedelta(days=random.randint(60, 350))
                deactivation_record = {
                    'provisioning_id': f'PROV{uuid.uuid4().hex[:8].upper()}',
                    'customer_id': contract['customer_id'],
                    'contract_id': contract['contract_id'],
                    'service_type': contract['service_type'],
                    'action': 'DEACTIVATE',
                    'action_date': deactivation_date,
                    'status': 'COMPLETED',
                    'requested_by': 'CUSTOMER',
                    'notes': f'{contract["service_type"]} service deactivated',
                }
                provisioning_records.append(deactivation_record)
        
        return pd.DataFrame(provisioning_records)
    
    def generate_usage_logs(self, contracts_df):
        """Generate usage logs for services"""
        usage_logs = []
        
        for _, contract in contracts_df.iterrows():
            if not contract['usage_based']:
                continue
                
            current_date = contract['start_date']
            while current_date <= min(contract['end_date'], self.end_date):
                # Generate daily usage (some days might have no usage)
                if random.random() < 0.8:  # 80% chance of usage on any given day
                    if contract['service_type'] == 'Internet':
                        usage_amount = random.uniform(5, 100)  # GB per day
                    elif contract['service_type'] == 'Phone':
                        usage_amount = random.uniform(10, 300)  # minutes per day
                    elif contract['service_type'] == 'Cloud_Storage':
                        usage_amount = random.uniform(1, 50)   # GB per day
                    elif contract['service_type'] == 'Email':
                        usage_amount = random.randint(1, 20)   # mailboxes
                    else:
                        usage_amount = 1  # subscription based
                    
                    usage_record = {
                        'usage_id': f'USAGE{uuid.uuid4().hex[:8].upper()}',
                        'customer_id': contract['customer_id'],
                        'contract_id': contract['contract_id'],
                        'service_type': contract['service_type'],
                        'usage_date': current_date,
                        'usage_amount': round(usage_amount, 2),
                        'usage_unit': contract['usage_unit'],
                        'rate_applied': contract['contracted_rate'] if not contract['usage_based'] else contract['overage_rate'],
                        'recorded_by': 'METERING_SYSTEM',
                    }
                    usage_logs.append(usage_record)
                
                current_date += timedelta(days=1)
        
        return pd.DataFrame(usage_logs)
    
    def generate_billing_data(self, contracts_df, usage_logs_df, customers_df):
        """Generate billing data with intentional discrepancies"""
        billing_records = []
        
        # Group usage by customer, contract, and month for billing
        usage_logs_df['billing_month'] = pd.to_datetime(usage_logs_df['usage_date']).dt.to_period('M')
        monthly_usage = usage_logs_df.groupby(['customer_id', 'contract_id', 'billing_month'])['usage_amount'].sum().reset_index()
        
        for _, contract in contracts_df.iterrows():
            current_month = pd.Period(contract['start_date'], freq='M')
            end_month = pd.Period(min(contract['end_date'], self.end_date), freq='M')
            
            while current_month <= end_month:
                # Get usage for this month
                month_usage = monthly_usage[
                    (monthly_usage['customer_id'] == contract['customer_id']) &
                    (monthly_usage['contract_id'] == contract['contract_id']) &
                    (monthly_usage['billing_month'] == current_month)
                ]
                
                total_usage = month_usage['usage_amount'].sum() if not month_usage.empty else 0
                
                # Calculate billing amount
                base_charge = contract['contracted_rate']
                
                # Apply promotional rate expiry (source of revenue leakage)
                billing_date = current_month.to_timestamp()
                if (contract['is_promotional'] and 
                    contract['promo_expiry_date'] and 
                    billing_date > contract['promo_expiry_date']):
                    # Should revert to regular rate, but sometimes doesn't (revenue leakage)
                    if random.random() < 0.3:  # 30% chance of missing rate change
                        rate_used = contract['contracted_rate']  # Keep using promo rate
                        rate_error = True
                    else:
                        rate_used = contract['base_rate'] * contract['tier_multiplier']
                        rate_error = False
                else:
                    rate_used = contract['contracted_rate']
                    rate_error = False
                
                # Calculate overage charges
                overage_charge = 0
                if contract['usage_based'] and total_usage > contract['included_usage']:
                    overage_usage = total_usage - contract['included_usage']
                    overage_charge = overage_usage * contract['overage_rate']
                
                total_amount = base_charge + overage_charge
                
                # Introduce billing errors intentionally
                billing_error_type = None
                
                # Missing charges (10% chance)
                if random.random() < 0.1:
                    total_amount = 0
                    billing_error_type = 'MISSING_CHARGE'
                
                # Incorrect rates (5% chance)
                elif random.random() < 0.05:
                    total_amount *= random.uniform(0.5, 0.9)  # Under-charge
                    billing_error_type = 'INCORRECT_RATE'
                    rate_error = True
                
                # Usage mismatch (8% chance) - bill for different usage
                elif random.random() < 0.08 and contract['usage_based']:
                    wrong_usage = total_usage * random.uniform(0.3, 0.8)
                    if wrong_usage > contract['included_usage']:
                        overage_charge = (wrong_usage - contract['included_usage']) * contract['overage_rate']
                    else:
                        overage_charge = 0
                    total_amount = base_charge + overage_charge
                    billing_error_type = 'USAGE_MISMATCH'
                
                billing_record = {
                    'billing_id': f'BILL{uuid.uuid4().hex[:8].upper()}',
                    'customer_id': contract['customer_id'],
                    'contract_id': contract['contract_id'],
                    'service_type': contract['service_type'],
                    'billing_month': current_month.strftime('%Y-%m'),
                    'billing_date': billing_date,
                    'base_charge': base_charge,
                    'usage_amount': total_usage,
                    'included_usage': contract['included_usage'],
                    'overage_usage': max(0, total_usage - contract['included_usage']) if contract['usage_based'] else 0,
                    'overage_charge': overage_charge,
                    'total_amount': round(total_amount, 2),
                    'rate_applied': rate_used,
                    'status': random.choice(['PAID', 'PAID', 'PAID', 'PENDING', 'OVERDUE']),
                    'due_date': billing_date + timedelta(days=30),
                    'billing_error_type': billing_error_type,
                    'rate_error': rate_error,
                }
                billing_records.append(billing_record)
                
                current_month += 1
        
        # Add some duplicate billing records (5% chance)
        duplicates = []
        for record in random.sample(billing_records, min(len(billing_records) // 20, 50)):
            duplicate = record.copy()
            duplicate['billing_id'] = f'BILL{uuid.uuid4().hex[:8].upper()}'
            duplicate['billing_error_type'] = 'DUPLICATE_ENTRY'
            duplicates.append(duplicate)
        
        billing_records.extend(duplicates)
        
        return pd.DataFrame(billing_records)
    
    def generate_all_data(self):
        """Generate all sample datasets"""
        print("Generating sample data for Revenue Leakage Detection System...")
        
        print("1. Generating customers...")
        customers_df = self.generate_customers()
        customers_df.to_csv(self.output_dir / 'customers.csv', index=False)
        print(f"   Generated {len(customers_df)} customers")
        
        print("2. Generating contracts...")
        contracts_df = self.generate_contracts(customers_df)
        contracts_df.to_csv(self.output_dir / 'contracts.csv', index=False)
        print(f"   Generated {len(contracts_df)} contracts")
        
        print("3. Generating provisioning records...")
        provisioning_df = self.generate_provisioning_records(contracts_df)
        provisioning_df.to_csv(self.output_dir / 'provisioning_records.csv', index=False)
        print(f"   Generated {len(provisioning_df)} provisioning records")
        
        print("4. Generating usage logs...")
        usage_logs_df = self.generate_usage_logs(contracts_df)
        usage_logs_df.to_csv(self.output_dir / 'usage_logs.csv', index=False)
        print(f"   Generated {len(usage_logs_df)} usage records")
        
        print("5. Generating billing data...")
        billing_df = self.generate_billing_data(contracts_df, usage_logs_df, customers_df)
        billing_df.to_csv(self.output_dir / 'billing_data.csv', index=False)
        print(f"   Generated {len(billing_df)} billing records")
        
        # Generate data summary
        summary = {
            'generation_date': datetime.now().isoformat(),
            'datasets': {
                'customers': {
                    'records': len(customers_df),
                    'file': 'customers.csv',
                    'description': 'Customer master data with tiers and status'
                },
                'contracts': {
                    'records': len(contracts_df),
                    'file': 'contracts.csv',
                    'description': 'Service contracts with pricing and terms'
                },
                'provisioning_records': {
                    'records': len(provisioning_df),
                    'file': 'provisioning_records.csv',
                    'description': 'Service activation/deactivation records'
                },
                'usage_logs': {
                    'records': len(usage_logs_df),
                    'file': 'usage_logs.csv',
                    'description': 'Daily service usage measurements'
                },
                'billing_data': {
                    'records': len(billing_df),
                    'file': 'billing_data.csv',
                    'description': 'Monthly billing records with intentional errors'
                }
            },
            'intentional_errors': {
                'missing_charges': 'Approximately 10% of billing records',
                'incorrect_rates': 'Approximately 5% of billing records',
                'usage_mismatches': 'Approximately 8% of billing records',
                'duplicate_entries': 'Approximately 50 duplicate records',
                'rate_expiry_errors': 'Promotional rates not updated after expiry'
            },
            'statistics': {
                'total_customers': len(customers_df),
                'total_contracts': len(contracts_df),
                'total_billing_records': len(billing_df),
                'total_usage_records': len(usage_logs_df),
                'date_range': f'{self.start_date.strftime("%Y-%m-%d")} to {self.end_date.strftime("%Y-%m-%d")}'
            }
        }
        
        with open(self.output_dir / 'data_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSample data generation complete!")
        print(f"Files saved to: {self.output_dir}")
        print(f"Total records generated: {sum([len(customers_df), len(contracts_df), len(provisioning_df), len(usage_logs_df), len(billing_df)])}")
        print("\nData Summary:")
        for dataset, info in summary['datasets'].items():
            print(f"  {dataset}: {info['records']} records - {info['description']}")
        
        print("\nIntentional Revenue Leakage Scenarios:")
        for error_type, description in summary['intentional_errors'].items():
            print(f"  • {error_type.replace('_', ' ').title()}: {description}")

if __name__ == "__main__":
    generator = SampleDataGenerator(num_customers=1000, num_months=12)
    generator.generate_all_data()
