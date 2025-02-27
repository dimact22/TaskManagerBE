# Import required modules for MongoDB and environment variable management
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

# Create a MongoDB client instance using the URI
mongo_uri = os.getenv("MONGO_URL")

# Access the "azubi_wohnen" database
client = MongoClient(mongo_uri)


# Define collections for apartments, users, and temporary users
users = client.get_database("azubi_wohnen")
users_collections = users.get_collection("AllUsers")
groups = users.get_collection("AllGroups")
tasks = users.get_collection("Tasks")
completedtasks = users.get_collection("CompletedTask")

