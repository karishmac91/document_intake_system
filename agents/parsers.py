import mimetypes
import pdfplumber
#import pytesseract
import easyocr
from PIL import Image
from PIL import Image
import re, os
from pathlib import Path


def parse_files(file_paths):
    """
    Parses a list of file paths and returns structured content and metadata for each.
    Supports PDF and JPEG/JPG formats.
    """
    
    if isinstance(file_paths, (Path, str)):
        raise ValueError("Expected a list of file paths, got a single path. Wrap it in a list.")
    
    print("Parsing files:", file_paths)
    parsed_results = []
    
    for file_path in file_paths:
        #normalized_path = os.path.normpath(file_path)
        #mime_type, _ = mimetypes.guess_type(normalized_path)
        #print(f"Detected MIME type for {normalized_path}: {mime_type}")
        #print(f"Detected MIME type for {file_path}: {mime_type}")
        
        print(f"This is the file path: {file_path}")

        path = Path(file_path).resolve()  # normalize and get absolute path

        mime_type, _ = mimetypes.guess_type(path.as_uri() if path.exists() else path.name)

        print(f"Detected MIME type for {path}: {mime_type}")
        
        
        if mime_type == 'application/pdf':
            print(f"Parsing PDF file: {file_path}")
            #parsed = parse_pdf(normalized_path)
            parsed = parse_pdf(str(path))         

        elif mime_type in ['image/jpeg', 'image/jpg']:
            print(f"Parsing JPEG file: {file_path}")
            # Check if the file exists before parsing
            
            parsed = parse_jpeg(str(path))
        else:
            parsed = {
                "type": "unsupported",
                "file": path,
                "filename": path.name,
                "content": "",
                "metadata": {"error": "Unsupported file type"}
            }

        parsed["file"] = str(path)  # include file path in result
        parsed_results.append(parsed)
        print(f"Parsed result for {file_path}: {parsed}")
    print("Completed parsing all files.")
    return parsed_results

def parse_pdf(file_path):
    content = ""
    metadata = {}
    transactions = []
    print(f"Parsing PDF file: {file_path}")

    try:
        with pdfplumber.open(file_path) as pdf:
            metadata["pages"] = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                content += page.extract_text() or ""

         # Extract header information
        metadata.update(extract_account_info(content))

        # Extract transactions
        transactions = extract_transactions(content)    

    except Exception as e:
        metadata["error"] = str(e)

    return {
        "type": "bank_statement",
        "content": content.strip(),
        "metadata": metadata,
        "transactions": transactions
    }





def extract_account_info(text):
    info = {}
    patterns = {
        "account_holder": r"Account Holder:\s*(.*)",
        "account_number": r"Account Number:\s*(\d+)",
        "iban": r"IBAN:\s*([A-Z0-9]+)",
        "currency": r"Currency:\s*(\w+)",
        "statement_period": r"Statement Period:\s*([\d\-A-Za-z\s]+)",
        "starting_balance": r"Starting Balance:\s*([\d,\.]+) AED",
        "ending_balance": r"Ending Balance:\s*([\d,\.]+) AED"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            info[key] = match.group(1).strip()

    return info

def extract_transactions(text):
    transactions = []

    # Skip to the part after the header line
    lines = text.splitlines()
    start_idx = -1
    for i, line in enumerate(lines):
        if "Date Description" in line and "Balance" in line:
            start_idx = i + 1
            break

    if start_idx == -1:
        return transactions

    txn_lines = lines[start_idx:]

    txn_pattern = re.compile(
        r"(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([\d\.]+)?\s+([\d\.]+)?\s+([\d\.]+)"
    )

    for line in txn_lines:
        match = txn_pattern.match(line)
        if match:
            date, desc, debit, credit, balance = match.groups()
            transactions.append({
                "date": date,
                "description": desc.strip(),
                "debit": float(debit) if debit else 0.0,
                "credit": float(credit) if credit else 0.0,
                "balance": float(balance)
            })

    return transactions


def parse_jpeg(file_path):
    content = ""
    metadata = {}
    print(f"Inside parse_JPEG file: {file_path}")
    try:
        image = Image.open(file_path)
        metadata["format"] = image.format
        metadata["size"] = image.size
        metadata["mode"] = image.mode

        # Use EasyOCR for text extraction
        reader = easyocr.Reader(['en'])  # Add other language codes if needed
        print("Starting OCR on image...")
         # Perform OCR
        result = reader.readtext(file_path, detail=0)
        print(f"result : {result}")  # detail=0 returns text only
        content = "\n".join(result)
        print(f"Extracted content: {content}")

    except Exception as e:
        metadata["error"] = str(e)

    return {
        "type": "jpg",
        "content": content.strip(),
        "metadata": metadata
    }


import re

'''def extract_emirates_id_fields(raw_text: str) -> dict:
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    result = {
        "name": None,
        "id_number": None,
        "nationality": None,
        "address": None,
        "raw_text": raw_text
    }

    for i, line in enumerate(lines):
        # Extract ID Number
        if 'id number' in line.lower():
            # Check next line for actual number
            for j in range(i + 1, min(i + 3, len(lines))):
                match = re.search(r'\d{3}-\d{4}-\d{7}-\d', lines[j])
                if match:
                    result["id_number"] = match.group()
                    break

        # Extract Name
        elif 'name' in line.lower():
            parts = line.split(':')
            if len(parts) > 1:
                result["name"] = parts[1].strip()
            elif i + 1 < len(lines):
                result["name"] = lines[i + 1].strip()

        # Extract Nationality
        elif 'nationality' in line.lower():
            parts = line.split(':')
            if len(parts) > 1:
                result["nationality"] = parts[1].strip()
            elif i + 1 < len(lines):
                result["nationality"] = lines[i + 1].strip()

        # Heuristic Address Detection (very weak)
        elif 'address' in line.lower() or 'P.O.' in line:
            result["address"] = line.strip()

    return result '''
