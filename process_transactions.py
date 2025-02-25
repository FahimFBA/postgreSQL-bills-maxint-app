import csv
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

def parse_date(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y')

def format_date(date):
    return date.strftime('%Y-%m-%d')

def format_created_at(time_str):
    try:
        # Assuming the time is in the format "HH:MM.S"
        now = datetime.now()
        time_parts = time_str.split('.')
        hours, minutes = map(int, time_parts[0].split(':'))
        seconds = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # Ensure hours are within 0-23 range
        hours = hours % 24
        
        return now.replace(hour=hours, minute=minutes, second=seconds, microsecond=0).isoformat()
    except (ValueError, IndexError):
        # If there's any error in parsing, return the current timestamp
        return datetime.now().isoformat()

def calculate_average_interval(dates):
    if len(dates) < 2:
        return None
    intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
    return sum(intervals) / len(intervals)

def predict_next_payment_date(last_date, avg_interval):
    if avg_interval is None:
        return None
    return last_date + timedelta(days=avg_interval)

def process_transactions(input_file, output_file):
    transactions = defaultdict(list)
    
    # Read the CSV file and group transactions
    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = ['id', 'created_at', 'external_id', 'type', 'amount', 'date', 'description', 'category', 'counter_party', 'recurring', 'tag', 'account_external_id', 'location', 'predicted_next_payment']
        
        for row in reader:
            key = (row['description'], row['category'])  # Group by description and category
            transactions[key].append(row)
    
    # Process transactions and write to new CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for key, group in transactions.items():
            is_recurring = len(group) > 1 and len(set([t['amount'] for t in group])) <= 2  # Allow small variations in amount
            dates = sorted([parse_date(t['date']) for t in group])
            avg_interval = calculate_average_interval(dates) if is_recurring else None
            
            for transaction in group:
                new_transaction = {
                    'id': str(uuid.uuid4()),
                    'created_at': format_created_at(transaction['createdAt']),
                    'external_id': transaction['externalId'],
                    'type': transaction['type'],
                    'amount': float(transaction['amount']),
                    'date': format_date(parse_date(transaction['date'])),
                    'description': transaction['description'],
                    'category': transaction['category'],
                    'counter_party': transaction['counterParty'],
                    'recurring': 'true' if is_recurring else 'false',
                    'tag': transaction['tag'],
                    'account_external_id': transaction['accountExternalId'],
                    'location': transaction['location'],
                    'predicted_next_payment': None
                }
                
                if is_recurring:
                    last_date = parse_date(transaction['date'])
                    next_payment = predict_next_payment_date(last_date, avg_interval)
                    new_transaction['predicted_next_payment'] = format_date(next_payment) if next_payment else None
                
                writer.writerow(new_transaction)

if __name__ == "__main__":
    input_file = "Maxint-accounts-9999-demo.csv"
    output_file = "processed_transactions.csv"
    process_transactions(input_file, output_file)
    print(f"Processed transactions saved to {output_file}")
