require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_API_KEY);

async function queryRecurringBillsDirect() {
    try {
        // Step 1: Get all transactions
        const { data: transactions, error: transactionError } = await supabase
            .from('transactions')
            .select('*')
            .order('date', { ascending: true });

        if (transactionError) throw transactionError;

        // Step 2: Process transactions to find recurring bills
        const transactionMap = new Map();
        transactions.forEach(transaction => {
            if (!transactionMap.has(transaction.description)) {
                transactionMap.set(transaction.description, []);
            }
            transactionMap.get(transaction.description).push(transaction);
        });

        const recurringBills = [];
        for (const [description, group] of transactionMap.entries()) {
            if (group.length > 1) {
                const sortedDates = group.map(t => new Date(t.date)).sort((a, b) => a - b);
                const intervals = [];
                for (let i = 1; i < sortedDates.length; i++) {
                    intervals.push((sortedDates[i] - sortedDates[i-1]) / (1000 * 60 * 60 * 24));
                }
                const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
                const avgAmount = group.reduce((sum, t) => sum + t.amount, 0) / group.length;

                if (avgInterval > 0 && avgInterval <= 366) {
                    const lastTransaction = group[group.length - 1];
                    recurringBills.push({
                        amount: Number(avgAmount.toFixed(2)),
                        description,
                        date: lastTransaction.date,
                        nextDate: new Date(new Date(lastTransaction.date).getTime() + avgInterval * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                        occurrence_count: group.length,
                        avg_interval_days: Math.round(avgInterval),
                        predicted_next_payment: lastTransaction.predicted_next_payment
                    });
                }
            }
        }

        // Sort recurring bills
        recurringBills.sort((a, b) => b.occurrence_count - a.occurrence_count);

        console.log('Recurring bills:');
        console.log(JSON.stringify(recurringBills, null, 2));
    } catch (error) {
        console.error('Error querying recurring bills:', error);
    }
}

queryRecurringBillsDirect();
