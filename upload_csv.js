require('dotenv').config();
const fs = require('fs');
const { parse } = require('csv-parse');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_API_KEY);

const csvFilePath = './Maxint-accounts-9999-demo.csv';

fs.createReadStream(csvFilePath)
    .pipe(parse({ columns: true, trim: true }))
    .on('data', async (row) => {
        try {
            const { data, error } = await supabase
                .from('transactions')
                .insert(row);

            if (error) throw error;
            console.log('Inserted row:', data);
        } catch (error) {
            console.error('Error inserting row:', error);
        }
    })
    .on('end', () => {
        console.log('CSV file successfully processed');
    });