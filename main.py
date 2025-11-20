import os
from typing import List, Optional, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bson import ObjectId

from database import create_document, db
from schemas import DesignSession, StyleVariant, Customization

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Design Assistant Backend Ready"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# ----------------------
# API Models
# ----------------------
class ExtractedFeatures(BaseModel):
    pose: Optional[str] = None
    proportions: Optional[str] = None
    distinctive_features: Optional[List[str]] = None
    color_palette: Optional[List[str]] = None

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None

class UpdateCustomizationRequest(BaseModel):
    pose_change: Optional[str] = None
    background: Optional[str] = None
    composition: Optional[str] = None
    narrative: Optional[str] = None

class GenerateVariantsRequest(BaseModel):
    variations: List[StyleVariant]

# ----------------------
# Helper
# ----------------------
COLLECTION = "designsession"  # from DesignSession class name lowercased

def compute_label(variant: StyleVariant) -> str:
    return f"{variant.format} | {variant.art_style} | {variant.color_palette}"

def oid(session_id: str) -> ObjectId:
    try:
        return ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session id")

# ----------------------
# Routes
# ----------------------
@app.post("/api/session", response_model=Dict)
async def create_session(payload: CreateSessionRequest):
    session = DesignSession(title=payload.title or "Untitled Session")
    inserted_id = create_document(COLLECTION, session)
    return {"id": inserted_id, "status": session.status}

@app.post("/api/session/{session_id}/upload")
async def upload_reference(session_id: str, files: List[UploadFile] = File(...)):
    # In a real app, we'd upload to storage and analyze; here we'll fake URLs and extracted features
    image_urls = [f"/uploads/{f.filename}" for f in files]
    # Simple mock features
    features = {
        "pose": "as in reference",
        "proportions": "consistent",
        "distinctive_features": ["hair style", "outfit elements"],
        "color_palette": ["#ffcc00", "#3366ff"]
    }
    result = db[COLLECTION].update_one({"_id": oid(session_id)}, {"$set": {"reference_images": image_urls, "extracted_features": features}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"reference_images": image_urls, "extracted_features": features}

@app.post("/api/session/{session_id}/customize")
async def apply_customization(session_id: str, payload: UpdateCustomizationRequest):
    customization = Customization(**payload.model_dump(exclude_none=True))
    result = db[COLLECTION].update_one({"_id": oid(session_id)}, {"$set": {"customization": customization.model_dump(), "status": "customized"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "customized", "customization": customization.model_dump()}

@app.post("/api/session/{session_id}/generate")
async def generate_variations(session_id: str, payload: GenerateVariantsRequest):
    # Compute labels and mock asset urls
    saved_vars = []
    for v in payload.variations:
        label = compute_label(v)
        saved_vars.append({**v.model_dump(), "label": label, "asset_url": f"/assets/mock/{label.replace(' | ', '_').lower()}.png"})
    result = db[COLLECTION].update_one({"_id": oid(session_id)}, {"$set": {"variations": saved_vars, "status": "rendered"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "rendered", "variations": saved_vars}

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    doc = db[COLLECTION].find_one({"_id": oid(session_id)})
    if not doc:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    doc["_id"] = str(doc["_id"])  # make serializable
    return doc

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
