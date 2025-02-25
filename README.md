# postgreSQL-bills
Create a PostgreSQL view that aggregates bank transaction data to identify recurring bill payments.

### Given
A [CSV file](https://github.com/maxint-app/postgreSQL-bills/blob/main/Maxint-accounts-9999-demo.csv) containing bank transaction data with columns: id, createdAt, externalId, type, amount, date, description, category, counterParty, recurring, tag, accountExternalId, and location.

### Goal
Generate a view with the following columns:
* amount: The amount due for the bill.
* description: The name or description of the transaction.
* nextDate: The predicted date for the next bill payment.
* date: The date the bill was last paid.

### Assumptions
The recurring column indicates whether a transaction is recurring.
Transactions with the same description and amount are likely recurring bills.
A reasonable method for predicting the next payment date is to calculate the average interval between payments for recurring transactions.

### Challenges
Determining the appropriate criteria for identifying recurring transactions.
Handling edge cases, such as transactions with irregular payment intervals or those that have recently started or stopped recurring.
Ensuring the view's performance, especially for large datasets.

### Deliverables
A PostgreSQL view that efficiently generates the desired output.
Documentation explaining the view's logic and assumptions.
Unit tests to verify the view's correctness.
