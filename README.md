# PostgreSQL Bills Analysis

This project provides a solution for identifying recurring bill payments from bank transaction data stored in a PostgreSQL database using Supabase.

## Overview

Instead of using a PostgreSQL view, we've implemented a JavaScript-based solution that offers more flexibility in identifying recurring bills and handling various edge cases.

## Key Features

- Identifies recurring bills based on transaction descriptions and intervals
- Calculates average amounts for recurring bills
- Predicts next payment dates
- Provides occurrence count and average interval for each recurring bill

## Getting Started

1. Clone this repository using `git clone https://github.com/FahimFBA/postgreSQL-bills-maxint-app.git`
2. Navigate to the project directory: `cd postgreSQL-bills-maxint-app`
3. Install dependencies: `npm install`
4. Set up your Supabase credentials in a `.env` file
5. Find out recurring status and create a new CSV file using `python process_transactions.py`
6. Create a new table in Supabase using the schema
   ```sql
   CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    external_id VARCHAR(255),
    type VARCHAR(50),
    amount DECIMAL(10, 2),
    date DATE,
    description TEXT,
    category VARCHAR(50),
    counter_party VARCHAR(255),
    recurring BOOLEAN,
    tag VARCHAR(50),
    account_external_id VARCHAR(255),
    location VARCHAR(255),
    predicted_next_payment DATE
    );
    ```
7. Upload the CSV file to Supabase using `node upload_csv.js`
8. Create an updated recurring bill view in Supabase using the following schema
   ```sql
    CREATE OR REPLACE VIEW recurring_bills_v2 AS
    WITH transaction_counts AS (
        SELECT
            description,
            COUNT(*) as occurrence_count,
            MIN(date::date) as first_date,
            MAX(date::date) as last_date,
            AVG(amount::numeric) as avg_amount
        FROM
            transactions
        GROUP BY
            description
    ),
    avg_intervals AS (
        SELECT
            tc.description,
            tc.occurrence_count,
            tc.first_date,
            tc.last_date,
            tc.avg_amount,
            CASE 
                WHEN tc.occurrence_count > 1 
                THEN (tc.last_date - tc.first_date)::float / (tc.occurrence_count - 1)
                ELSE NULL
            END AS avg_interval_days
        FROM
            transaction_counts tc
    )
    SELECT
        ROUND(ai.avg_amount::numeric, 2) as amount,
        ai.description,
        (ai.last_date + (ROUND(ai.avg_interval_days) * INTERVAL '1 day'))::date AS nextDate,
        ai.last_date::date AS date
    FROM
        avg_intervals ai
    WHERE
        ai.occurrence_count > 1
        AND ai.avg_interval_days BETWEEN 1 AND 366
    ORDER BY
        ai.description, ai.last_date DESC;
   ```
9. Run the `node query_recurring_bills_direct.js` script to get the recurring bills view.

## Unit Tests

We have implemented two sets of unit tests to verify the correctness of our implementation:

### 1. Transaction Processing Tests

These tests verify the correctness of our transaction processing logic. To run these tests:

1. Ensure you have Python installed on your system.
2. Navigate to the project directory in your terminal.
3. Run the following command:

   ```
   python -m unittest test_process_transactions.py
   ```

The tests cover various aspects of the transaction processing, including:
- Date parsing and formatting
- Calculation of average intervals between transactions
- Prediction of next payment dates
- Overall transaction processing logic

### 2. Recurring Bills View Tests

These tests verify the correctness of the recurring bills view logic. To run these tests:

1. Ensure you have Python installed on your system.
2. Navigate to the project directory in your terminal.
3. Run the following command:

   ```
   python -m unittest test_recurring_bills_view.py
   ```

The `test_recurring_bills_view.py` file contains tests that simulate the logic of the `recurring_bills_v2` view. These tests cover:
- Identification of recurring bills
- Handling of non-recurring transactions
- Calculation of average amounts for bills with varying amounts
- Prediction of next payment dates for recurring bills

Key features of these tests:
- They simulate the view logic in Python, allowing for fast and reliable testing without database dependencies.
- The tests use a `simulate_recurring_bills_view` method that mimics the SQL view's logic.
- Test data is created within the test methods, allowing for controlled and reproducible test scenarios.
- The tests verify both the structure (e.g., correct fields are present) and the content (e.g., correct calculations) of the simulated view results.

Note: These tests do not require a connection to the Supabase database. They are designed to verify the correctness of the view's logic independently of the database implementation, making them true unit tests.

By running both `test_process_transactions.py` and `test_recurring_bills_view.py`, you can ensure that both the transaction processing logic and the recurring bills identification logic are working correctly.

## View Logic and Assumptions

The recurring bills view (`recurring_bills_v2`) is implemented as a PostgreSQL view. Here's an explanation of its logic and assumptions:

1. **Transaction Grouping**: Transactions are grouped by their description, assuming that recurring bills will have consistent descriptions.

2. **Occurrence Count**: The view counts the number of occurrences for each unique description. It assumes that recurring bills will have multiple occurrences.

3. **Date Range**: The view calculates the first and last date for each group of transactions with the same description.

4. **Average Amount**: It calculates the average amount for each group, assuming that recurring bills may have slight variations in amount.

5. **Average Interval**: The view calculates the average interval between transactions by dividing the total date range by the number of occurrences minus one. This assumes that recurring bills occur at roughly regular intervals.

6. **Next Date Prediction**: The next expected date for a bill is predicted by adding the rounded average interval to the last known date.

7. **Filtering Criteria**:
   - Only groups with more than one occurrence are considered recurring.
   - The average interval must be between 1 and 366 days, assuming bills recur at least annually but not more frequently than daily.

These assumptions help identify likely recurring bills, but may not capture all edge cases or irregular payment patterns.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
