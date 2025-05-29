from crewai import Agent

def create_orchestrator_agent():
    return Agent(
        role='Orchestrator',
        goal='Coordinate document processing pipeline',
        backstory='Experienced system architect that knows how to manage pipelines and assign tasks to specialists.'
    )

def create_ingestion_agent():
    return Agent(
        role='Ingestion Agent',
        goal='Read and classify documents, extract structured metadata and transactions',
        backstory='Expert in OCR, document parsing, and data extraction.'
    )

def create_validation_agent():
    return Agent(
        role='Validation Agent',
        goal='Validate extracted data for integrity and compliance',
        backstory='Thorough validator who ensures documents follow structure and rules.'
    )

def create_decision_agent():
    return Agent(
        role='Decision Agent',
        goal='Route validated data to the correct database system',
        backstory='Intelligent agent that matches data types to the appropriate storage system.'

    )

