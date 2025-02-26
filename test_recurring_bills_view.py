import unittest
from datetime import datetime, timedelta

class TestRecurringBillsView(unittest.TestCase):
    def simulate_recurring_bills_view(self, transactions):
        # This method simulates the logic of the recurring_bills_v2 view
        grouped_transactions = {}
        for transaction in transactions:
            key = transaction['description']
            if key not in grouped_transactions:
                grouped_transactions[key] = []
            grouped_transactions[key].append(transaction)

        recurring_bills = []
        for description, group in grouped_transactions.items():
            if len(group) > 1:
                dates = sorted([datetime.fromisoformat(t['date']) for t in group])
                amounts = [t['amount'] for t in group]
                avg_amount = sum(amounts) / len(amounts)
                avg_interval = (dates[-1] - dates[0]).days / (len(dates) - 1)

                if 1 <= avg_interval <= 366:
                    recurring_bills.append({
                        "amount": round(avg_amount, 2),
                        "description": description,
                        "nextDate": (dates[-1] + timedelta(days=round(avg_interval))).date().isoformat(),
                        "date": dates[-1].date().isoformat()
                    })

        return recurring_bills

    def test_recurring_bills_identification(self):
        test_data = [
            {
                "external_id": "1",
                "type": "DEBIT",
                "amount": 100,
                "date": (datetime.now() - timedelta(days=60)).date().isoformat(),
                "description": "Monthly Subscription",
                "category": "Subscriptions",
                "counter_party": "Netflix",
                "recurring": True,
            },
            {
                "external_id": "2",
                "type": "DEBIT",
                "amount": 100,
                "date": (datetime.now() - timedelta(days=30)).date().isoformat(),
                "description": "Monthly Subscription",
                "category": "Subscriptions",
                "counter_party": "Netflix",
                "recurring": True,
            },
            {
                "external_id": "3",
                "type": "DEBIT",
                "amount": 100,
                "date": datetime.now().date().isoformat(),
                "description": "Monthly Subscription",
                "category": "Subscriptions",
                "counter_party": "Netflix",
                "recurring": True,
            },
        ]

        result = self.simulate_recurring_bills_view(test_data)

        self.assertEqual(len(result), 1)  # Should identify one recurring bill
        bill = result[0]
        self.assertEqual(bill["description"], "Monthly Subscription")
        self.assertEqual(bill["amount"], 100)
        self.assertIsNotNone(bill["nextDate"])
        self.assertEqual(bill["date"], datetime.now().date().isoformat())

    def test_non_recurring_transactions(self):
        test_data = [
            {
                "external_id": "1",
                "type": "DEBIT",
                "amount": 50,
                "date": (datetime.now() - timedelta(days=60)).date().isoformat(),
                "description": "One-time Purchase",
                "category": "Shopping",
                "counter_party": "Amazon",
                "recurring": False,
            },
            {
                "external_id": "2",
                "type": "DEBIT",
                "amount": 75,
                "date": (datetime.now() - timedelta(days=30)).date().isoformat(),
                "description": "Another Purchase",
                "category": "Shopping",
                "counter_party": "Walmart",
                "recurring": False,
            },
        ]

        result = self.simulate_recurring_bills_view(test_data)

        self.assertEqual(len(result), 0)  # Should not identify any recurring bills

    def test_varying_amounts(self):
        test_data = [
            {
                "external_id": "1",
                "type": "DEBIT",
                "amount": 95,
                "date": (datetime.now() - timedelta(days=60)).date().isoformat(),
                "description": "Utility Bill",
                "category": "Utilities",
                "counter_party": "Power Company",
                "recurring": True,
            },
            {
                "external_id": "2",
                "type": "DEBIT",
                "amount": 105,
                "date": (datetime.now() - timedelta(days=30)).date().isoformat(),
                "description": "Utility Bill",
                "category": "Utilities",
                "counter_party": "Power Company",
                "recurring": True,
            },
            {
                "external_id": "3",
                "type": "DEBIT",
                "amount": 100,
                "date": datetime.now().date().isoformat(),
                "description": "Utility Bill",
                "category": "Utilities",
                "counter_party": "Power Company",
                "recurring": True,
            },
        ]

        result = self.simulate_recurring_bills_view(test_data)

        self.assertEqual(len(result), 1)  # Should identify one recurring bill
        bill = result[0]
        self.assertEqual(bill["description"], "Utility Bill")
        self.assertEqual(bill["amount"], 100)  # Should be the average of the amounts
        self.assertIsNotNone(bill["nextDate"])
        self.assertEqual(bill["date"], datetime.now().date().isoformat())

if __name__ == "__main__":
    unittest.main()
