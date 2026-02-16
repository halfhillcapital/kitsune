import pathlib

import logfire
import marimo
import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic_ai.ui.ag_ui import AGUIAdapter

from kitsune.agents.marimo import create_agent, create_deps

logfire.configure()
logfire.instrument_pydantic_ai()

app = FastAPI(title="Kitsune")

agent = create_agent()
deps = create_deps()

chat = agent.to_web(deps=deps)


@app.get("/health")
async def health():
    return {"status": "ok"}


# AG-UI chat endpoint
@app.post("/ag-ui")
async def ag_ui(request: Request) -> Response:
    return await AGUIAdapter.dispatch_request(request, agent=agent, deps=deps)


# Notebook listing
@app.get("/notebooks")
async def list_notebooks():
    nb_dir = pathlib.Path("notebooks")
    if not nb_dir.exists():
        return []
    return [
        {"name": p.stem, "path": f"/notebooks/{p.stem}"}
        for p in sorted(nb_dir.glob("*.py"))
    ]


# Mount marimo notebooks in run mode
_nb_dir = pathlib.Path("notebooks")
if _nb_dir.exists():
    _marimo_app = marimo.create_asgi_app()
    for nb in sorted(_nb_dir.glob("*.py")):
        _marimo_app = _marimo_app.with_app(path=f"/{nb.stem}", root=str(nb))
    app.mount("/notebooks", _marimo_app.build())

if __name__ == "__main__":
    uvicorn.run("main:chat", host="0.0.0.0", port=8010, reload=True)
