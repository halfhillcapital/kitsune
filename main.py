import pathlib
from contextlib import asynccontextmanager

import logfire
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

from kitsune.agents.marimo import create_agent, create_deps
from kitsune.services.sandbox import SandboxManager

logfire.configure()
logfire.instrument_pydantic_ai()

sandbox = SandboxManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await sandbox.startup()
    yield
    await sandbox.shutdown()


app = FastAPI(title="Kitsune", lifespan=lifespan)

agent = create_agent()


@app.get("/health")
async def health():
    return {"status": "ok"}


# Vercel AI chat endpoint
@app.post("/chat")
async def chat(request: Request) -> Response:
    # TODO: extract session_id from auth/header once auth is wired up
    session_id = request.headers.get("x-session-id", "default")
    deps = create_deps(session_id=session_id, sandbox=sandbox)
    return await VercelAIAdapter.dispatch_request(request, agent=agent, deps=deps)


# Notebook listing (scoped to session)
@app.get("/notebooks")
async def list_notebooks(request: Request):
    session_id = request.headers.get("x-session-id", "default")
    nb_dir = sandbox.get_user_dir(session_id)
    if not nb_dir.exists():
        # Fall back to template notebooks
        nb_dir = pathlib.Path("notebooks")
    if not nb_dir.exists():
        return []
    return [
        {"name": p.stem, "path": f"/notebooks/{p.stem}"}
        for p in sorted(nb_dir.glob("*.py"))
    ]


# Get or create sandbox container, return marimo edit URL
@app.get("/notebooks/{session_id}")
async def get_notebook_url(session_id: str):
    info = await sandbox.get_or_create(session_id)
    return {"url": f"http://localhost:{info.host_port}"}


static_dir = pathlib.Path("static")
if static_dir.exists():
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)
