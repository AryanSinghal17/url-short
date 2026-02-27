from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pymongo.errors import DuplicateKeyError
from typing import List
import os

from database import url_collection, create_indexes
from models import URLDBModel
from schemas import URLCreate, URLResponse
from utils import generate_short_code

app = FastAPI(title="Minimal URL Shortener API")

# Setup CORS for frontend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await create_indexes()

@app.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def create_url(url_data: URLCreate):
    """
    Generate a short code for the original url and save to db.
    """
    max_retries = 10
    
    for _ in range(max_retries):
        short_code = generate_short_code()
        
        # Check if it already exists to be safe
        existing = await url_collection.find_one({"short_code": short_code})
        if not existing:
            new_url = URLDBModel(
                original_url=url_data.original_url,
                short_code=short_code,
                click_count=0
            )
            
            try:
                # Insert the document
                inserted_doc = await url_collection.insert_one(new_url.model_dump())
                
                # Retrieve the inserted doc
                created_doc = await url_collection.find_one({"_id": inserted_doc.inserted_id})
                return URLResponse(**created_doc)

            except DuplicateKeyError:
                # Just in case our check passed but another process inserted
                continue
            
    raise HTTPException(status_code=500, detail="Could not generate unique short code")

@app.get("/urls", response_model=List[URLResponse])
async def list_urls():
    """
    List all generated URLs
    """
    urls = []
    cursor = url_collection.find().sort("created_at", -1)
    async for document in cursor:
        urls.append(URLResponse(**document))
    return urls

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    """
    Redirect shortened url to original url
    """
    url_doc = await url_collection.find_one({"short_code": short_code})
    if url_doc:
        # Increment click count asynchronously in the background
        await url_collection.update_one(
            {"short_code": short_code},
            {"$inc": {"click_count": 1}}
        )
        return RedirectResponse(
            url_doc["original_url"],
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
        
    raise HTTPException(status_code=404, detail="URL not found")

@app.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(short_code: str):
    """
    Delete a specific URL by short code
    """
    result = await url_collection.delete_one({"short_code": short_code})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="URL not found")
    return None
