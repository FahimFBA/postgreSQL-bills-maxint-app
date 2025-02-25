require('dotenv').config();
const fs = require('fs');
const { parse } = require('csv-parse');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_API_KEY);

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_API_KEY) {
    console.error('Error: SUPABASE_URL or SUPABASE_API_KEY is not set in the environment variables.');
    process.exit(1);
}

const csvFilePath = './processed_transactions.csv';

let totalRows = 0;
let successfulInserts = 0;
let failedInserts = 0;

function formatRow(row) {
    const formattedRow = {};
    for (const [key, value] of Object.entries(row)) {
        if (key === 'recurring') {
            formattedRow[key] = value.toLowerCase() === 'true';
        } else if (key === 'amount') {
            formattedRow[key] = value ? parseFloat(value) : null;
        } else if (key === 'predicted_next_payment') {
            formattedRow[key] = value || null;
        } else {
            formattedRow[key] = value;
        }
    }
    return formattedRow;
}

async function processCSV() {
    return new Promise((resolve, reject) => {
        const parser = parse({
            columns: true,
            trim: true
        });

        const rows = [];

        fs.createReadStream(csvFilePath)
            .pipe(parser)
            .on('data', (row) => {
                rows.push(row);
            })
            .on('end', async () => {
                console.log('CSV file reading completed');
                console.log(`Total rows read: ${rows.length}`);

                const processRow = async (row) => {
                    totalRows++;
                    try {
                        const formattedRow = formatRow(row);
                        const { data, error } = await supabase
                            .from('transactions')
                            .upsert(formattedRow, { onConflict: 'id', returning: 'minimal' });

                        if (error) {
                            throw error;
                        } else {
                            successfulInserts++;
                        }
                    } catch (error) {
                        failedInserts++;
                        console.error(`Error inserting row ${totalRows}:`);
                        console.error('Error details:', error);
                        console.error('Row data:', row);
                    }
                };

                await Promise.all(rows.map(processRow));

                console.log('CSV processing completed');
                console.log(`Total rows processed: ${totalRows}`);
                console.log(`Successful inserts: ${successfulInserts}`);
                console.log(`Failed inserts: ${failedInserts}`);

                if (failedInserts > 0) {
                    console.error('Some rows failed to insert. Please check the Supabase table schema and ensure all required columns exist.');
                }
                resolve();
            })
            .on('error', (error) => {
                console.error('Error reading CSV file:', error);
                reject(error);
            });
    });
}

processCSV()
    .then(() => {
        console.log('CSV processing completed successfully.');
    })
    .catch((error) => {
        console.error('An error occurred during CSV processing:', error);
    });
