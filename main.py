from typing import Optional
import os
import io
import csv
from math import ceil
from datetime import datetime, timedelta

import pandas as pd
from bson import ObjectId
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import (
    RedirectResponse,
    StreamingResponse
)
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient, DESCENDING


# =====================================================
# CONFIG
# =====================================================

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://user1:hSa1x0LsPPgzZBBf@cluster0.iiyxgtt.mongodb.net/?appName=Cluster0"
)

DB_NAME = os.getenv(
    "MONGODB_DB",
    "yellowpages_db"
)

COLLECTION_NAME = os.getenv(
    "MONGODB_COLLECTION",
    "businesses"
)

PAGE_SIZE_OPTIONS = [25, 50, 100, 250]

# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Yellow Pages Admin Dashboard"
)

templates = Jinja2Templates(
    directory="templates"
)

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

collection = db[COLLECTION_NAME]


# =====================================================
# INDEXES
# =====================================================

try:
    collection.create_index("unique_key", unique=True)
except Exception:
    pass

collection.create_index("name")
collection.create_index("phone")
collection.create_index("website")
collection.create_index("search_location")
collection.create_index("search_term")
collection.create_index("scraped_at")


# =====================================================
# HELPERS
# =====================================================

def to_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def to_object_id(id_value: str):

    if not ObjectId.is_valid(id_value):

        raise HTTPException(
            status_code=400,
            detail="Invalid document id"
        )

    return ObjectId(id_value)


def build_search_query(
    q=None,
    location=None,
    has_website=None
):
    query = {}

    filters = []

    if q:

        filters.append(
            {
                "$or": [
                    {"name": {"$regex": q, "$options": "i"}},
                    {"phone": {"$regex": q, "$options": "i"}},
                    {"address": {"$regex": q, "$options": "i"}},
                    {"details": {"$regex": q, "$options": "i"}},
                    {"website": {"$regex": q, "$options": "i"}},
                ]
            }
        )

    if location:

        filters.append(
            {
                "search_location": {
                    "$regex": location,
                    "$options": "i"
                }
            }
        )

    if has_website == "yes":

        filters.append(
            {
                "website": {
                    "$exists": True,
                    "$ne": ""
                }
            }
        )

    if has_website == "no":

        filters.append(
            {
                "$or": [
                    {"website": ""},
                    {"website": {"$exists": False}}
                ]
            }
        )

    if filters:
        query["$and"] = filters

    return query


# =====================================================
# DASHBOARD
# =====================================================

@app.get("/")
def home(
    request: Request,
    q: Optional[str] = None,
    location: Optional[str] = None,
    has_website: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):

    if page_size not in PAGE_SIZE_OPTIONS:
        page_size = 50

    query = build_search_query(
        q,
        location,
        has_website
    )

    total_records = collection.count_documents(query)

    total_pages = max(
        1,
        ceil(total_records / page_size)
    )

    page = max(
        1,
        min(page, total_pages)
    )

    skip = (page - 1) * page_size

    docs = [
        to_doc(doc)
        for doc in collection.find(query)
        .sort("_id", DESCENDING)
        .skip(skip)
        .limit(page_size)
    ]

    today = datetime.utcnow().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    stats = {
        "total": 0,
        "website": 0,
        "phone": 0,
        "today": 0
    }
    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={
            "records": docs,
            "stats": stats,
    
            "query": q or "",
            "location": location or "",
            "has_website": has_website or "",
    
            "page": page,
            "page_size": page_size,
            "page_size_options": PAGE_SIZE_OPTIONS,
    
            "total_records": total_records,
            "total_pages": total_pages
        }
    )

# =====================================================
# CREATE
# =====================================================

@app.post("/create")
def create_record(
    name: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    details: str = Form(""),
    website: str = Form("")
):

    collection.insert_one(
        {
            "name": name,
            "phone": phone,
            "address": address,
            "details": details,
            "website": website,
            "created_at": datetime.utcnow()
        }
    )

    return RedirectResponse(
        url="/",
        status_code=303
    )


# =====================================================
# UPDATE
# =====================================================

@app.post("/update/{record_id}")
def update_record(
    record_id: str,
    name: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    details: str = Form(""),
    website: str = Form("")
):

    result = collection.update_one(
        {
            "_id":
            to_object_id(record_id)
        },
        {
            "$set":
            {
                "name": name,
                "phone": phone,
                "address": address,
                "details": details,
                "website": website
            }
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return RedirectResponse(
        "/",
        status_code=303
    )


# =====================================================
# DELETE
# =====================================================

@app.post("/delete/{record_id}")
def delete_record(record_id: str):

    collection.delete_one(
        {
            "_id":
            to_object_id(record_id)
        }
    )

    return RedirectResponse(
        "/",
        status_code=303
    )


# =====================================================
# BULK DELETE
# =====================================================

@app.post("/bulk-delete")
async def bulk_delete(request: Request):

    form = await request.form()

    ids = form.getlist("selected_ids")

    object_ids = [
        to_object_id(x)
        for x in ids
    ]

    collection.delete_many(
        {
            "_id":
            {
                "$in": object_ids
            }
        }
    )

    return RedirectResponse(
        "/",
        status_code=303
    )


# =====================================================
# EXPORT CSV
# =====================================================

@app.get("/export/csv")
def export_csv():

    docs = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    output = io.StringIO()

    if docs:

        writer = csv.DictWriter(
            output,
            fieldnames=docs[0].keys()
        )

        writer.writeheader()

        writer.writerows(docs)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=businesses.csv"
        }
    )


# =====================================================
# EXPORT EXCEL
# =====================================================

@app.get("/export/excel")
def export_excel():

    docs = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    df = pd.DataFrame(docs)

    stream = io.BytesIO()

    with pd.ExcelWriter(
        stream,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Businesses"
        )

    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=businesses.xlsx"
        }
    )