
import psycopg2
from psycopg2.extras import execute_values


import os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD')
)

def store_bank_statement(data: dict):
    
    cursor = conn.cursor()

    metadata = data.get("metadata", {})
    transactions = data.get("transactions", [])

    # Insert into bank_statements
    insert_stmt = """
        INSERT INTO bank_statements
        (account_holder, account_number, iban, currency, statement_period, starting_balance, ending_balance, file_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    try:
        cursor.execute(insert_stmt, (
            metadata.get("account_holder"),
            metadata.get("account_number"),
            metadata.get("iban"),
            metadata.get("currency"),
            metadata.get("statement_period"),
            metadata.get("starting_balance"),
            metadata.get("ending_balance"),
            metadata.get("file")
    ))
    except Exception as e:
     print("Error inserting bank statement:", e)
    
    statement_id = cursor.fetchone()[0]

    # Insert transactions
    if transactions:
        tx_insert = """
            INSERT INTO transactions
            (statement_id, date, description, debit, credit, balance)
            VALUES %s
        """
        tx_values = [
            (
                statement_id,
                tx.get("date"),
                tx.get("description"),
                tx.get("debit"),
                tx.get("credit"),
                tx.get("resulting_balance")

            )
            for tx in transactions
        ]
        execute_values(cursor, tx_insert, tx_values)

    conn.commit()
    cursor.close()
    conn.close()
