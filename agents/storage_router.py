

#from agents.orchestrator import extract_bank_statement_metadata, extract_bank_statement_transactions
from db.postgresql import store_bank_statement
import re
import datetime
from db.mongodb import store_json
#from db.qdrant import store_embedding
#from db.neo4j import create_entity_relationship

def store_data(parsed : dict):
    result_log = {}

    for doc in parsed:
      print(f"doc['type']: doc['type']")
      if doc['type'] == 'bank_statement':
        metadata = extract_bank_statement_metadata(doc['content'])
        transactions = extract_bank_statement_transactions(doc['content'])
        metadata["file"] = doc.get("file")  # required by DB insert

        data_to_store = {
            "metadata": metadata,
            "transactions": transactions
        }

        store_bank_statement(data_to_store)

        result_log[doc['type']] = "Stored in PostgreSQL"

      elif doc['type'] == "jpg" or doc['type'] == "jpeg":
       print(f"Storing JPEG file: {doc['content']}")
    
    # Convert content string into a dictionary
       json_data = {
        "raw_text": doc['content'],
        "file_path": doc.get('file'),
        "metadata": doc.get('metadata')
        }

       store_json("emirates_ids", json_data)
       result_log[doc['type']] = "Stored in MongoDB"

      else:
       result_log[doc['type']] = "Unrecognized document type skipped" 
            

    return result_log



def extract_bank_statement_metadata(text):
    def find(pattern, default=None):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default

    start_date, end_date = None, None
    match = re.search(r"Statement Period:\s*(\d{2}-\w{3}-\d{4})\s*to\s*(\d{2}-\w{3}-\d{4})", text)
    if match:
        start_date = match.group(1)
        end_date = match.group(2)

    return {
        "account_holder": find(r"Account Holder:\s*(.+)"),
        "account_number": find(r"Account Number:\s*(\d+)"),
        "iban": find(r"IBAN:\s*([A-Z0-9\s]+)"),
        "currency": find(r"Currency:\s*([A-Z]+)"),
        "statement_period": f"{start_date} to {end_date}",
        "starting_balance": float(find(r"Starting Balance:\s*([\d\.]+)", "0.0")),
        "ending_balance": float(find(r"Ending Balance:\s*([\d\.]+)", "0.0")),
    }

def extract_bank_statement_transactions(text):
    lines = text.splitlines()
    transactions = []
    for line in lines:
        match = re.match(r"(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([\d.]+)\s+([\d.]+)", line)
        if match:
            date, desc, amount1, amount2 = match.groups()
            # Heuristic
            debit, credit = (float(amount1), 0.0)
            if re.search(r"credit|salary|bonus|freelance", desc.lower()):
                credit, debit = float(amount1), 0.0
            transactions.append({
                "date": datetime.datetime.strptime(date, "%d-%m-%Y").date(),
                "description": desc.strip(),
                "debit": debit,
                "credit": credit,
                "resulting_balance": float(amount2)
            })
    return transactions
