from pymongo import MongoClient
from bson import ObjectId
from utils.constants import mongo_uri

# MongoDB Configuration
MONGO_URI = mongo_uri
DATABASE_NAME = "sample"

# Initialize MongoDB Client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def get_collection(collection_name):
    """Get a specific collection from the database."""
    return db[collection_name]

def serialize_document(document):
    """Convert MongoDB document to a dictionary with string ObjectId."""
    if document:
        document["_id"] = str(document["_id"])
    return document

# CRUD Operations

def insert_document(collection_name, data):
    """Insert a document into the specified collection."""
    collection = get_collection(collection_name)
    result = collection.insert_one(data)
    return str(result.inserted_id)

def get_all_documents(collection_name, limit=100):
    """Retrieve all documents from a collection with a limit."""
    collection = get_collection(collection_name)
    return [serialize_document(doc) for doc in collection.find().limit(limit)]

def get_document_by_id(collection_name, doc_id):
    """Retrieve a single document by ID."""
    collection = get_collection(collection_name)
    document = collection.find_one({"_id": ObjectId(doc_id)})
    return serialize_document(document)

def update_document(collection_name, doc_id, update_data):
    """Update a document by ID."""
    collection = get_collection(collection_name)
    result = collection.update_one({"_id": ObjectId(doc_id)}, {"$set": update_data})
    return result.modified_count > 0  # True if updated, False otherwise

def delete_document(collection_name, doc_id):
    """Delete a document by ID."""
    collection = get_collection(collection_name)
    result = collection.delete_one({"_id": ObjectId(doc_id)})
    return result.deleted_count > 0  # True if deleted, False otherwise

def delete_all(collection_name):
    collection = get_collection(collection_name)
    result = collection.delete_many({})
