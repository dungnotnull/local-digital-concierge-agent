
import sqlite3
import random
from datetime import datetime, timedelta

def generate_synthetic_bills(db_path: str = 'data/concierge.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure tables exist (they should from init)
    cursor.execute('SELECT COUNT(*) FROM bills')
    if cursor.fetchone()[0] > 0:
        print('Bills table already has data. Skipping generation.')
        return
    
    bill_types = ['electricity', 'water', 'internet', 'phone', 'rent', 'loan']
    issuers = {
        'electricity': ['EVN TP.HCM', 'EVN Ha Noi'],
        'water': ['SAWACo', 'Ha Noi Water'],
        'internet': ['VNPT', 'Viettel', 'FPT'],
        'phone': ['Viettel', 'VNPT', 'Mobifone'],
        'rent': ['Chu nha tro'],
        'loan': ['VCB', 'BIDV', 'Techcombank']
    }
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    
    for i in range(20):
        bill_type = random.choice(bill_types)
        issuer = random.choice(issuers[bill_type])
        amount = random.randint(100000, 5000000)  # 100k to 5M VND
        # Random date within range
        days_offset = random.randint(0, (end_date - start_date).days)
        due_date = start_date + timedelta(days=days_offset)
        # Billing period: previous month
        period_end = due_date - timedelta(days=1)
        period_start = period_end - timedelta(days=29)
        
        cursor.execute('''
            INSERT INTO bills (bill_type, issuer, account_number, amount_due, due_date,
                               billing_period_from, billing_period_to, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bill_type,
            issuer,
            f'{random.randint(10000000, 99999999)}',
            amount,
            due_date.strftime('%Y-%m-%d'),
            period_start.strftime('%Y-%m-%d'),
            period_end.strftime('%Y-%m-%d'),
            'pending'
        ))
    
    conn.commit()
    conn.close()
    print('Generated 20 synthetic bills.')

if __name__ == '__main__':
    generate_synthetic_bills()

