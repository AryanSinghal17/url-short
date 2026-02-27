import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# --- MOCK MONGODB DATABASE IMPLEMENTATION FOR LOCAL TESTING ---
# This is a temporary Drop-In Replacement for Motor to allow running without MongoDB
class MockCursor:
    def __init__(self, data):
        self.data = list(data)
    def sort(self, field, direction):
        if field == "created_at":
            self.data.sort(key=lambda x: x.get("created_at"), reverse=(direction == -1))
        return self
    async def __aiter__(self):
        for item in self.data:
            yield item

class MockCollection:
    def __init__(self):
        self._store = []
        self._counter = 1
        
    async def create_index(self, key, unique=False):
        pass
        
    async def find_one(self, query):
        for doc in self._store:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc.copy()
        return None
        
    async def insert_one(self, document):
        doc = document.copy()
        doc["_id"] = self._counter
        self._counter += 1
        self._store.append(doc)
        class InsertResult:
            inserted_id = doc["_id"]
        return InsertResult()
        
    def find(self, query=None):
        if query is None:
             query = {}
        result = []
        for doc in self._store:
             match = True
             for k, v in query.items():
                 if doc.get(k) != v:
                     match = False
                     break
             if match:
                 result.append(doc.copy())
        return MockCursor(result)
        
    async def update_one(self, query, update):
        for idx, doc in enumerate(self._store):
             match = True
             for k, v in query.items():
                 if doc.get(k) != v:
                     match = False
                     break
             if match:
                 # Apply basic $inc update
                 if "$inc" in update:
                     for field, amount in update["$inc"].items():
                          self._store[idx][field] = self._store[idx].get(field, 0) + amount
                 return
                 
    async def delete_one(self, query):
         for idx, doc in enumerate(self._store):
              match = True
              for k, v in query.items():
                  if doc.get(k) != v:
                      match = False
                      break
              if match:
                  self._store.pop(idx)
                  class DeleteResult:
                       deleted_count = 1
                  return DeleteResult()
         class DeleteResult:
              deleted_count = 0
         return DeleteResult()

url_collection = MockCollection()

async def get_database():
    pass

async def create_indexes():
    pass
