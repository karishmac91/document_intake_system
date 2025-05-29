from crewai import Agent, Task, Crew
from agents.parsers import parse_files  # Assuming you save it in parsers.py
import json


from agents.roles import (
    create_orchestrator_agent,
    create_ingestion_agent,
    create_validation_agent,
    create_decision_agent
)
from agents.storage_router import store_data
#from agents.storage_router import store_data


from pydantic import BaseModel

from pydantic import BaseModel
from typing import List, Optional

class Transaction(BaseModel):
    date: str
    description: str
    debit: float #Optional[float] = None
    credit: float #Optional[float] = None
    balance: float #Optional[float] = None

class Metadata(BaseModel):
    account_holder: str
    account_number: str
    iban: str
    currency: str
    statement_period: str
    starting_balance: float
    ending_balance: float

class IngestionOutput(BaseModel):
    
    metadata: Metadata
    transactions: List[Transaction]
    file: str  # Path or filename


class ValidationOutput(BaseModel):
    
    metadata: Metadata
    transactions: List[Transaction]
    file: str
    errors: Optional[List[str]] = None




class StorageConfirmation(BaseModel):
    storage: str
    reason: str

def run_pipeline1(file_paths: list[str]):
    print("Running pipeline with file paths:", file_paths)
    if not file_paths:
        raise ValueError("No file paths provided for processing.")
    
    orchestrator = create_orchestrator_agent()
    ingestion_agent = create_ingestion_agent()
    validation_agent = create_validation_agent()
    decision_agent = create_decision_agent()
    
    # Pre-parse file before passing to agents
    parsed = parse_files([file_paths])
    print("Parsed file content:", parsed)
    if not parsed:
        raise ValueError("No valid files parsed. Check file formats and content.")

    

    task1 = Task(
    description=(
        "You are given parsed file content in inputs['content']. "
        "Each item includes 'type', 'content', 'metadata', and 'file'.\n\n"

        "Your job is to extract structured data ONLY from the content — DO NOT guess or hallucinate any fields.\n"
        "Only return values that are explicitly present in the parsed content.\n"
        "If a field is missing or unclear, set it to null or 'unknown'.\n\n"

        "The expected fields are: account_holder, account_number, iban, currency, "
        "statement_period (with start_date and end_date), starting_balance, ending_balance, "
        "and a 'transactions' array with fields: date, description, debit, credit, resulting_balance.\n"

        "Be strict: do not invent any values. Only use what is clearly present in the parsed text.\n"
    ),
    expected_output=(
        "A structured JSON object including the extracted metadata and a 'transactions' array.\n"
        "Missing fields should be included with null or 'unknown' values, not omitted."
    ),
    agent=ingestion_agent,
    output_model=IngestionOutput
)



    task2 = Task(
    description=(
        "You are provided with structured data in inputs['content'].\n"
        "Your job is to validate that required fields are present: account_holder, account_number, iban, "
        "currency, starting_balance, ending_balance, and a transactions list with valid entries date, description, debit, credit, and resulting balance.\n"
        "If any fields are missing or invalid, include them in an 'errors' list."
    ),
    expected_output="Validated structured data. If errors are found, include them in an 'errors' field.",
    agent=validation_agent,
    output_model=ValidationOutput
)


  
    task3 = Task(
    description=(
        "You are provided with validated structured data in inputs['content'].\n"
        "Determine the appropriate storage system based on document type.\n"
        "Since this is a 'bank_statement', you should store it in a PostgreSQL database.\n"
        "Return a confirmation message including where the data should be stored and why."
    ),
    expected_output=(
        "Storage confirmation with rationale. e.g., "
        "'{\"storage\": \"PostgreSQL\", \"reason\": \"Structured tabular financial data\"}'"
    ),
    agent=decision_agent,
    output_model=StorageConfirmation  
)


    crew = Crew(
        agents=[orchestrator, ingestion_agent, validation_agent, decision_agent],
        tasks=[task1, task2, task3],
        verbose=True
    )

    print("Crew initialized with agents and tasks.")
    # Run the crew with the provided file paths
    result = crew.kickoff(inputs={"content": parsed})
    #final_task_output = result.tasks_output[-1]  # Last task output
    #print("Final raw output:", final_task_output.raw)
    #final_output_dict = json.loads(final_task_output.raw)




    #print("Type of result:", type(result))
    #print("Result dir:", dir(result))  # See all attributes/methods on CrewOutput
    #print("Result repr:", repr(result))
    print("Ingestion Output:", result.tasks_output[0].raw)

    for idx, task in enumerate(result.tasks_output):
     print(f"Task {idx} - Type: {type(task)}, Raw Output: {task.raw}")
     print(task.raw)

    validated_data_json = result.tasks_output[0].raw
    print("Validated data JSON:", validated_data_json)

    validated_data = json.loads(validated_data_json)
    print("Validated data:", validated_data)

# Pass structured dict with document type key expected by store_data
    storage_status = store_data({"bank_statement": validated_data})


    # Step 5: Store data
    #storage_status = store_data(result)
    return {
        "parsed_file": parsed,
        "pipeline_result": validated_data,
        "storage_status": storage_status
    }
    
