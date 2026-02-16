"""
Marimo notebook tools for the PydanticAI agent.
Provides tools to list, read, create/overwrite, and execute marimo notebooks.
"""

from __future__ import annotations

import importlib.util
import pathlib
import textwrap

from typing import Any, TypeVar

from pydantic import BaseModel, Field
from pydantic_ai import Agent


NOTEBOOKS_DIR = pathlib.Path("notebooks")

MARIMO_HEADER = """\
import marimo

__generated_with = "0.19.11"
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
    """Render a CellSpec into a marimo @app.cell decorated function."""
    params = ", ".join(cell.deps) if cell.deps else ""
    sig = f"def {cell.name}({params}):"

    # Indent the cell body by 4 spaces
    body = textwrap.indent(textwrap.dedent(cell.code).strip(), "    ")

    if cell.returns:
        ret = ", ".join(cell.returns)
        # Trailing comma for single-element tuple
        ret_line = f"    return ({ret},)" if len(cell.returns) == 1 else f"    return ({ret})"
    else:
        ret_line = "    return"

    return f"@app.cell\n{sig}\n{body}\n{ret_line}"


def _build_notebook(cells: list[CellSpec]) -> str:
    """Build a complete marimo .py notebook from cell specs."""
    parts = [MARIMO_HEADER]
    for cell in cells:
        parts.append("")
        parts.append(_cell_to_source(cell))
    parts.append("")
    parts.append("")
    parts.append(MARIMO_FOOTER)
    return "\n".join(parts) + "\n"


AgentDepsT = TypeVar("AgentDepsT")
AgentResultT = TypeVar("AgentResultT")
def with_notebooks(agent: Agent[AgentDepsT, AgentResultT]) -> Agent[AgentDepsT, AgentResultT]:
    """Register notebook tools on the agent."""

    @agent.tool_plain
    async def list_notebooks() -> list[dict[str, str]]:
        """List all marimo notebooks in the notebooks directory."""
        if not NOTEBOOKS_DIR.exists():
            return []
        return [
            {"name": p.stem, "path": str(p)}
            for p in sorted(NOTEBOOKS_DIR.glob("*.py"))
        ]

    @agent.tool_plain
    async def read_notebook(name: str) -> str:
        """Read the full source code of a marimo notebook by name (without .py extension)."""
        path = NOTEBOOKS_DIR / f"{name}.py"
        if not path.exists():
            return f"Error: notebook '{name}' not found."
        return path.read_text(encoding="utf-8")

    @agent.tool_plain
    async def write_notebook(name: str, cells: list[CellSpec]) -> str:
        """Create or overwrite a marimo notebook.

        Each cell needs: code (the Python source), deps (variables it reads
        from other cells), and returns (variables it defines for other cells).
        The first cell should typically import libraries.
        """
        NOTEBOOKS_DIR.mkdir(exist_ok=True)
        path = NOTEBOOKS_DIR / f"{name}.py"
        source = _build_notebook(cells)
        path.write_text(source, encoding="utf-8")
        return f"Notebook written to {path} ({len(cells)} cells)."

    @agent.tool_plain
    async def run_notebook(name: str) -> dict[str, Any]:
        """Execute a marimo notebook and return its cell outputs and defined variable names.

        Useful for verifying a notebook works or inspecting computed results.
        """
        path = NOTEBOOKS_DIR / f"{name}.py"
        if not path.exists():
            return {"error": f"Notebook '{name}' not found."}
        try:
            spec = importlib.util.spec_from_file_location(f"nb_{name}", str(path))
            if spec is None or spec.loader is None:
                return {"error": f"Could not load notebook '{name}'."}
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            outputs, defs = mod.app.run()
            return {
                "defined_vars": list(defs),
                "num_outputs": len(outputs),
                "output_types": [type(o).__name__ for o in outputs],
            }
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    return agent
