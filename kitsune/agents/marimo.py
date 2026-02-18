import re
import textwrap
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from kitsune.config import get_config
from kitsune.services.sandbox import SandboxManager

config = get_config()


# -- Deps --

@dataclass
class MarimoAgentDeps:
    session_id: str
    sandbox: SandboxManager


# -- Notebook builder helpers --

_MARIMO_VERSION = version("marimo")

MARIMO_HEADER = f"""\
import marimo

__generated_with = "{_MARIMO_VERSION}"
app = marimo.App(width="medium")
"""

MARIMO_FOOTER = """\
if __name__ == "__main__":
    app.run()
"""


class CellSpec(BaseModel):
    """Specification for a single marimo notebook cell."""

    code: str = Field(description="Python code for the cell body.")
    deps: list[str] = Field(
        default_factory=list,
        description="Variable names this cell needs from other cells (become function params).",
    )
    returns: list[str] = Field(
        default_factory=list,
        description="Variable names this cell exports (become the return tuple).",
    )
    name: str = Field(
        default="_",
        description="Optional cell function name. Use '_' for anonymous.",
    )


def _cell_to_source(cell: CellSpec) -> str:
    params = ", ".join(cell.deps) if cell.deps else ""
    sig = f"def {cell.name}({params}):"
    body = textwrap.indent(textwrap.dedent(cell.code).strip(), "    ")

    if cell.returns:
        ret = ", ".join(cell.returns)
        ret_line = f"    return ({ret},)" if len(cell.returns) == 1 else f"    return ({ret})"
    else:
        ret_line = "    return"

    return f"@app.cell\n{sig}\n{body}\n{ret_line}"


def _build_notebook(cells: list[CellSpec]) -> str:
    parts = [MARIMO_HEADER]
    for cell in cells:
        parts.append("")
        parts.append(_cell_to_source(cell))
    parts.append("")
    parts.append("")
    parts.append(MARIMO_FOOTER)
    return "\n".join(parts) + "\n"


# -- Agent + Tools --

model = OpenAIChatModel(
    provider=OpenAIProvider(base_url=config.LOCAL_URL),
    model_name=config.LOCAL_MODEL,
)

agent = Agent(
    model=model,
    deps_type=MarimoAgentDeps,
    instructions=(
        "You are Kitsune, an AI data analysis assistant. "
        "You can create and run marimo notebooks for interactive data analysis. "
        "When asked to analyze data or create visualizations, write a marimo notebook "
        "using the write_notebook tool, then run it with run_notebook to verify it works."
    ),
)


def _user_dir(ctx: RunContext[MarimoAgentDeps]):
    return ctx.deps.sandbox.get_user_dir(ctx.deps.session_id)


def _safe_name(name: str) -> str:
    """Sanitize notebook name to prevent directory traversal."""
    # Strip path separators and keep only safe characters
    base = name.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    base = base.removesuffix(".py")
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", base):
        raise ValueError(f"Invalid notebook name: {name!r}")
    return base


@agent.tool
async def list_notebooks(ctx: RunContext[MarimoAgentDeps]) -> list[dict[str, str]]:
    """List all marimo notebooks in the user's notebook directory."""
    nb_dir = _user_dir(ctx)
    if not nb_dir.exists():
        return []
    return [
        {"name": p.stem, "path": str(p.name)}
        for p in sorted(nb_dir.glob("*.py"))
    ]


@agent.tool
async def read_notebook(ctx: RunContext[MarimoAgentDeps], name: str) -> str:
    """Read the full source code of a marimo notebook by name (without .py extension)."""
    name = _safe_name(name)
    path = _user_dir(ctx) / f"{name}.py"
    if not path.exists():
        return f"Error: notebook '{name}' not found."
    return path.read_text(encoding="utf-8")


@agent.tool
async def write_notebook(ctx: RunContext[MarimoAgentDeps], name: str, cells: list[CellSpec]) -> str:
    """Create or overwrite a marimo notebook.

    Each cell needs: code (the Python source), deps (variables it reads
    from other cells), and returns (variables it defines for other cells).
    The first cell should typically import libraries.
    """
    name = _safe_name(name)
    nb_dir = _user_dir(ctx)
    nb_dir.mkdir(parents=True, exist_ok=True)
    path = nb_dir / f"{name}.py"
    source = _build_notebook(cells)
    path.write_text(source, encoding="utf-8")
    return f"Notebook written to {path.name} ({len(cells)} cells)."


@agent.tool
async def run_notebook(ctx: RunContext[MarimoAgentDeps], name: str) -> dict[str, Any]:
    """Execute a marimo notebook inside the user's sandbox container and return output.

    Useful for verifying a notebook works or inspecting computed results.
    """
    name = _safe_name(name)
    nb_dir = _user_dir(ctx)
    path = nb_dir / f"{name}.py"
    if not path.exists():
        return {"error": f"Notebook '{name}' not found."}

    try:
        await ctx.deps.sandbox.get_or_create(ctx.deps.session_id)
        output = await ctx.deps.sandbox.exec_in_container(
            ctx.deps.session_id,
            ["marimo", "run", "--headless", f"/notebooks/{name}.py"],
        )
        return {"status": "ok", "output": output}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def create_deps(session_id: str, sandbox: SandboxManager) -> MarimoAgentDeps:
    return MarimoAgentDeps(session_id=session_id, sandbox=sandbox)


def create_agent() -> Agent[MarimoAgentDeps]:
    return agent
