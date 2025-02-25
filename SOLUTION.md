# PostgreSQL Recurring Bill Payments View in Supabase

This solution creates a PostgreSQL view that aggregates bank transaction data to identify recurring bill payments, hosted on Supabase.

## Supabase Setup and Data Import

Follow these steps to set up your project in Supabase:

1. Create a Supabase account:
   - Go to https://supabase.com/ and sign up for an account if you haven't already.

2. Create a new project:
   - Click on "New Project" in the Supabase dashboard.
   - Choose a name for your project and set a secure database password.
   - Select the region closest to you or your users.
   - Click "Create new project" and wait for it to be set up.

3. Access SQL Editor:
   - In your project dashboard, go to the "SQL Editor" section.

4. Create the transactions table:
   - Copy and paste the following SQL into the SQL Editor:


First, we need to create a table to store the transaction data and import the CSV file:

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    external_id TEXT,
    type TEXT,
    amount NUMERIC(10, 2),
    date DATE,
    description TEXT,
    category TEXT,
    counter_party TEXT,
    recurring BOOLEAN,
    tag TEXT,
    account_external_id TEXT,
    location TEXT
);

-- Import data from CSV file
-- Assuming the CSV file is accessible to the PostgreSQL server
COPY transactions FROM '/path/to/Maxint-accounts-9999-demo.csv' WITH CSV HEADER;
```

5. Import data:
   - In the Supabase dashboard, go to the "Table Editor" section.
   - Click on the "transactions" table.
   - Click on "Import data" and select "CSV" as the file type.
   - Upload your Maxint-accounts-9999-demo.csv file.
   - Map the CSV columns to the table columns and click "Import".

6. Create the view:
   - Go back to the SQL Editor.
   - Copy and paste the following SQL to create the recurring_bills view:


```sql
CREATE OR REPLACE VIEW recurring_bills AS
WITH recurring_transactions AS (
    SELECT
        description,
        amount,
        date,
        LAG(date) OVER (PARTITION BY description, amount ORDER BY date) AS prev_date,
        LEAD(date) OVER (PARTITION BY description, amount ORDER BY date) AS next_date
    FROM transactions
    WHERE amount > 0 -- Only consider outgoing transactions
),
bill_intervals AS (
    SELECT
        description,
        amount,
        date,
        next_date,
        next_date - date AS interval
    FROM recurring_transactions
    WHERE prev_date IS NOT NULL -- Ensure we have at least 3 occurrences
      AND next_date IS NOT NULL
),
avg_intervals AS (
    SELECT
        description,
        amount,
        AVG(interval) AS avg_interval,
        COUNT(*) AS occurrence_count
    FROM bill_intervals
    GROUP BY description, amount
    HAVING COUNT(*) >= 2 -- Require at least 3 total occurrences (2 intervals)
      AND STDDEV(interval) <= 5 -- Ensure consistent intervals (allow 5 days of variance)
)
SELECT
    t.amount,
    t.description,
    t.date AS last_payment_date,
    t.date + (ai.avg_interval * INTERVAL '1 day') AS next_predicted_date
FROM transactions t
JOIN avg_intervals ai ON t.description = ai.description AND t.amount = ai.amount
WHERE t.date = (
    SELECT MAX(date)
    FROM transactions t2
    WHERE t2.description = t.description AND t2.amount = t.amount
)
ORDER BY next_predicted_date;
```

## View Logic and Assumptions

1. We consider transactions with positive amounts as potential bills (outgoing payments).
2. We group transactions by description and amount to identify recurring patterns.
3. We calculate the intervals between consecutive occurrences of the same transaction (description and amount).
4. We consider a transaction as recurring if:
   a. It occurs at least 3 times (2 intervals between 3 occurrences).
   b. The standard deviation of the intervals is no more than 5 days, ensuring consistency.
5. We calculate the average interval for each recurring transaction.
6. We predict the next payment date based on the last occurrence and the average interval.

## Using the View in Supabase

Now that you have set up the view in Supabase, you can use it in various ways:

1. SQL Editor:
   - In the SQL Editor, you can run queries directly on the recurring_bills view:

   ```sql
   -- Get all recurring bills
   SELECT * FROM recurring_bills;

   -- Get bills due in the next 30 days
   SELECT * FROM recurring_bills
   WHERE next_predicted_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '30 days');

   -- Get bills for a specific description
   SELECT * FROM recurring_bills
   WHERE description ILIKE '%Phone bill%';
   ```

2. API:
   - Supabase automatically generates API endpoints for your tables and views.
   - In the Supabase dashboard, go to the "API" section to find example code for querying your view using various programming languages.

3. Supabase Client Libraries:
   - You can use Supabase client libraries in your application to query the view.
   - Here's an example using JavaScript:

   ```javascript
   import { createClient } from '@supabase/supabase-js'

   const supabase = createClient('YOUR_SUPABASE_URL', 'YOUR_SUPABASE_ANON_KEY')

   async function getRecurringBills() {
     const { data, error } = await supabase
       .from('recurring_bills')
       .select('*')
     
     if (error) console.error('Error:', error)
     else console.log('Recurring bills:', data)
   }

   getRecurringBills()
   ```

## Optimizations and Considerations for Large Datasets in Supabase

1. Indexing: Create indexes on the `description`, `amount`, and `date` columns of the `transactions` table to improve query performance.

```sql
CREATE INDEX idx_transactions_desc_amount_date ON transactions (description, amount, date);
```

2. Partitioning: For very large datasets, consider partitioning the `transactions` table by date range to improve query performance and manageability.

3. Materialized View: If the underlying data doesn't change frequently, consider using a materialized view instead of a regular view. This will store the result set, improving query performance at the cost of data freshness.

```sql
CREATE MATERIALIZED VIEW recurring_bills_mv AS
SELECT * FROM recurring_bills;

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW recurring_bills_mv;
```

4. Incremental Updates: Implement a system to incrementally update the recurring bills information instead of recalculating everything for each query. This could involve storing intermediate results and updating them as new transactions are added.

5. Parallel Query Execution: Ensure that your PostgreSQL server is configured to use parallel query execution for complex queries on large datasets.

6. Regular Maintenance: Implement regular database maintenance tasks such as vacuuming and analyzing to keep statistics up-to-date and improve query planning.

By implementing these optimizations, the recurring bill identification system should be able to handle large datasets efficiently while providing accurate and timely information about recurring bill payments.

## Security Considerations

When working with Supabase:

1. Row Level Security (RLS):
   - Implement RLS policies to control access to your data at the row level.
   - Example policy to only allow authenticated users to view their own transactions:

   ```sql
   ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can view own transactions" ON transactions
     FOR SELECT
     USING (auth.uid() = user_id);
   ```

2. API Security:
   - Use Supabase's built-in authentication system to secure your API endpoints.
   - Never expose your service_role key; use the anon key for client-side applications.

3. Environment Variables:
   - Store sensitive information like API keys and database credentials as environment variables in your application, not in your source code.

By following these steps and considerations, you'll have a secure and efficient recurring bill identification system hosted on Supabase, accessible via SQL and API endpoints.
