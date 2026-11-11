from pathlib import Path
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .graph import run_research

app = FastAPI(
    title="ResearchCrew",
    description="Multi-Agent AI Research Assistant",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


INDEX = Path(__file__).parent / "static" / "index.html"


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/research")
def research(request: ResearchRequest):
    return run_research(request.topic)


@app.get("/")
def home():
    return FileResponse(INDEX)
