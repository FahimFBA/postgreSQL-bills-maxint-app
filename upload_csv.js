require('dotenv').config();
const fs = require('fs');
const { parse } = require('csv-parse');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_API_KEY);

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_API_KEY) {
    console.error('Error: SUPABASE_URL or SUPABASE_API_KEY is not set in the environment variables.');
    process.exit(1);
}

const csvFilePath = './Maxint-accounts-9999-demo.csv';

let totalRows = 0;
let successfulInserts = 0;
let failedInserts = 0;

function parseDate(dateString) {
    const [day, month, year] = dateString.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
}

function formatRow(row) {
    const formattedRow = { ...row };
    if (formattedRow.date) {
        formattedRow.date = parseDate(formattedRow.date);
    }
    if (formattedRow.recurring !== undefined) {
        formattedRow.recurring = formattedRow.recurring === 'true';
    }
    // Convert amount to a number
    if (formattedRow.amount) {
        formattedRow.amount = parseFloat(formattedRow.amount);
    }
    return formattedRow;
}

async function processCSV() {
    return new Promise((resolve, reject) => {
        fs.createReadStream(csvFilePath)
            .pipe(parse({
                columns: (headers) => {
                    // Remove BOM from the first column name
                    if (headers.length > 0 && headers[0].charCodeAt(0) === 0xFEFF) {
                        headers[0] = headers[0].slice(1);
                    }
                    // Convert all headers to lowercase
                    return headers.map(h => h.toLowerCase());
                },
                trim: true
            }))
            .on('data', async (row) => {
                totalRows++;
                try {
                    const formattedRow = formatRow(row);
                    console.log('Formatted row:', formattedRow);
                    const { data, error } = await supabase
                        .from('transactions')
                        .upsert(formattedRow, { onConflict: 'id', returning: 'minimal' });

                    if (error) {
                        throw error;
                    } else {
                        successfulInserts++;
                        console.log(`Upserted row ${totalRows}: Success`);
                    }
                } catch (error) {
                    failedInserts++;
                    console.error(`Error inserting row ${totalRows}:`);
                    console.error('Error details:', error);
                    console.error('Row data:', row);
                }
            })
            .on('end', () => {
                console.log('CSV file processing completed');
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
