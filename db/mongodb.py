from pymongo import MongoClient
import os

#MongoDB (e.g., Emirates ID, Credit Reports) for unstructured/semi-structured documents

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["document_intake"]

# List all databases
print(client.list_database_names())

# List collections in the selected database
print(db.list_collection_names())

def store_json(collection: str, data: dict):
    db[collection].insert_one(data)
    print(f"Data stored in MongoDB collection '{collection}': {data}")