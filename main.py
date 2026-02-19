import asyncio
import json
import pathlib
from contextlib import asynccontextmanager

import logfire
import uvicorn
import watchfiles
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic_ai.ui.vercel_ai import VercelAIAdapter
from sse_starlette.sse import EventSourceResponse

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

#TODO: add auth and session management to these endpoints as well, and enforce that users can only access their own sandbox/notebooks
@app.get("/sandbox/status")
async def sandbox_status():
    return sandbox.status()


def _list_notebooks(nb_dir: pathlib.Path) -> list[dict]:
    """List .py notebooks in nb_dir, falling back to templates if none exist."""
    if not nb_dir.exists() or not any(nb_dir.glob("*.py")):
        nb_dir = pathlib.Path("notebooks")
    if not nb_dir.exists():
        return []
    return [
        {"name": p.stem, "path": f"/notebooks/{p.stem}"}
        for p in sorted(nb_dir.glob("*.py"))
    ]


# Notebook listing (scoped to session)
@app.get("/notebooks")
async def list_notebooks(request: Request):
    session_id = request.headers.get("x-session-id", "default")
    nb_dir = sandbox.get_user_dir(session_id)
    return _list_notebooks(nb_dir)


# SSE endpoint that pushes notebook list updates when .py files change.
# EventSource can't send custom headers, so session_id is passed as a query
# param here only — intentional divergence from the header-based pattern.
@app.get("/notebooks/watch")
async def watch_notebooks(request: Request, session_id: str):
    nb_dir = sandbox.get_user_dir(session_id)
    nb_dir.mkdir(parents=True, exist_ok=True)  # awatch requires path to exist

    async def generator():
        stop = asyncio.Event()

        async def _watch_disconnect():
            while not await request.is_disconnected():
                await asyncio.sleep(0.5)
            stop.set()

        asyncio.create_task(_watch_disconnect())

        # Emit current list immediately so the client doesn't wait for a change
        yield {"data": json.dumps(_list_notebooks(nb_dir))}

        async for changes in watchfiles.awatch(nb_dir, stop_event=stop):
            if any(str(p).endswith(".py") for _, p in changes):
                yield {"data": json.dumps(_list_notebooks(nb_dir))}

    return EventSourceResponse(generator())


# Get or create sandbox container, return marimo edit URL
@app.get("/notebooks/{session_id}")
async def get_notebook_url(session_id: str):
    info = await sandbox.get_or_create(session_id)
    return {"url": f"http://localhost:{info.host_port}"}


static_dir = pathlib.Path("static")
if static_dir.exists():
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8010)
