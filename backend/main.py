"""FastAPI backend for personnel-scene data analytics with LLM-powered AI analysis."""
import json
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from pydantic import BaseModel
from config import LLMConfig, load_config, save_config
from services.llm_service import analyze_data, test_connection

app = FastAPI(title="Personnel Scene Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "dist")


# ---- API Routes (must be before SPA catch-all) ----

class LLMConfigBody(BaseModel):
    provider: str
    api_key: str
    base_url: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096


@app.get("/api/llm/config")
async def get_llm_config():
    cfg = load_config()
    return cfg.model_dump()


@app.post("/api/llm/config")
async def set_llm_config(body: LLMConfigBody):
    cfg = LLMConfig(**body.model_dump())
    save_config(cfg)
    return {"success": True}


@app.post("/api/llm/test")
async def test_llm():
    return await test_connection()


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    try:
        if ext == "json":
            data = json.loads(contents.decode("utf-8"))
            records = data if isinstance(data, list) else data.get("records") or data.get("data") or [data]
        elif ext == "csv":
            text = contents.decode("utf-8-sig")
            lines = [l for l in text.strip().split("\n") if l.strip()]
            headers = lines[0].split(",")
            records = [{headers[i]: vals[i] if i < len(vals) else "" for i in range(len(headers))} for line in lines[1:] if (vals := line.split(","))]
        else:
            raise HTTPException(400, f"Unsupported format: {ext}")
        return {"success": True, "records": records, "rowCount": len(records)}
    except Exception as e:
        raise HTTPException(400, f"Parse failed: {str(e)}")


class AnalysisRequest(BaseModel):
    module: str
    data: Any


@app.post("/api/analyze")
async def run_analysis(body: AnalysisRequest):
    return await analyze_data(body.module, body.data)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ---- SPA Fallback (catch-all, AFTER all API routes) ----

@app.get("/assets/{filename:path}")
async def serve_assets(filename: str):
    path = os.path.join(FRONTEND_DIR, "assets", filename)
    if os.path.isfile(path):
        return FileResponse(path)
    raise HTTPException(404)


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    file_path = os.path.join(FRONTEND_DIR, full_path) if full_path else os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
