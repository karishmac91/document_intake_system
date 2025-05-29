from agents.parsers import parse_files  # Assuming you save it in parsers.py
import json
from agents.storage_router import store_data
#from postgres import store_bank_statement  # Adjust import path as needed
from datetime import datetime
import re








def run_pipeline(file_paths: list[str]):
    print("Running pipeline with file paths:", file_paths)
    
    if not file_paths:
        raise ValueError("No file paths provided for processing.")
    
    parsed = parse_files([file_paths])

    print("Parsed file content:", parsed)

    if not parsed:
        raise ValueError("No valid files parsed. Check file formats and content.")
    
    store_data(parsed)
                    
    return {
        "parsed_file": parsed,
        #"pipeline_result": validated_data,
        #"storage_status": storage_status
    }




