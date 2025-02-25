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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
