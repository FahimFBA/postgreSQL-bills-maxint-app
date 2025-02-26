import unittest
from datetime import datetime, timedelta
from process_transactions import (
    parse_date,
    format_date,
    format_created_at,
    calculate_average_interval,
    predict_next_payment_date,
    process_transactions
)
import os
import csv

class TestProcessTransactions(unittest.TestCase):

    def test_parse_date(self):
        self.assertEqual(parse_date('01/02/2023'), datetime(2023, 2, 1))

    def test_format_date(self):
        self.assertEqual(format_date(datetime(2023, 2, 1)), '2023-02-01')

    def test_format_created_at(self):
        # Test with valid time string
        result = format_created_at('14:30.5')
        self.assertTrue(result.endswith('T14:30:05'))

        # Test with invalid time string
        result = format_created_at('invalid')
        self.assertTrue(datetime.fromisoformat(result))

    def test_calculate_average_interval(self):
        dates = [datetime(2023, 1, 1), datetime(2023, 2, 1), datetime(2023, 3, 1)]
        self.assertEqual(calculate_average_interval(dates), 30)

        # Test with less than 2 dates
        self.assertIsNone(calculate_average_interval([datetime(2023, 1, 1)]))

    def test_predict_next_payment_date(self):
        last_date = datetime(2023, 3, 1)
        avg_interval = 30
        self.assertEqual(predict_next_payment_date(last_date, avg_interval), datetime(2023, 3, 31))

        # Test with None avg_interval
        self.assertIsNone(predict_next_payment_date(last_date, None))

    def test_process_transactions(self):
        # Create a test input file
        test_input = 'test_input.csv'
        with open(test_input, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['externalId', 'createdAt', 'type', 'amount', 'date', 'description', 'category', 'counterParty', 'tag', 'accountExternalId', 'location'])
            writer.writerow(['1', '12:00.0', 'DEBIT', '100', '01/01/2023', 'Test Transaction', 'Test Category', 'Test Party', 'Test Tag', 'ACC1', 'Test Location'])
            writer.writerow(['2', '12:00.0', 'DEBIT', '100', '01/02/2023', 'Test Transaction', 'Test Category', 'Test Party', 'Test Tag', 'ACC1', 'Test Location'])

        # Process the test input
        test_output = 'test_output.csv'
        process_transactions(test_input, test_output)

        # Check if the output file was created
        self.assertTrue(os.path.exists(test_output))

        # Read the output and check its contents
        with open(test_output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['recurring'], 'true')
            self.assertIsNotNone(rows[0]['predicted_next_payment'])

        # Clean up test files
        os.remove(test_input)
        os.remove(test_output)

if __name__ == '__main__':
    unittest.main()
