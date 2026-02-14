# Marimo Integration Plan (Brainstorm)

## Requirements
- Embed Marimo notebooks in the NiceGUI app
- Per-user isolation (each user gets own notebook kernel)
- Notebooks run computations like backtests (CPU-heavy)
- Under 10 concurrent users expected

## Options Considered

### Option A: ASGI Mount (single process)
Use `marimo.create_asgi_app()` mounted on NiceGUI's underlying FastAPI app.

- **Pros:** single process, single port, no CORS, shared auth, simple deployment
- **Cons:** heavy backtests share resources with main app (chat may lag), tighter coupling
- **Per-user isolation:** Marimo natively creates separate kernels per browser session — works out of the box
- **Code sketch:**
  ```python
  import marimo
  from nicegui import app as nicegui_app

  marimo_app = marimo.create_asgi_app()
  marimo_app = marimo_app.with_app(path="/notebook", root="./notebooks/backtest.py")
  nicegui_app.mount("/marimo", marimo_app.build())
  ```

### Option B: Separate Process + iframe (multi-process)
Run Marimo as its own server, embed via iframe in NiceGUI.

- **Pros:** full resource isolation, heavy computations don't affect main app, can restart notebooks independently
- **Cons:** two processes to manage, need CORS config, separate auth, multiple ports
- **Per-user isolation:** Marimo handles this natively per connection
- **Could spawn per-user Marimo instances** for stronger isolation (but more complex)

## Recommendation
Start with **Option A (ASGI mount)** for simplicity. If backtests cause performance issues for the main app, migrate to **Option B**. The iframe approach in the NiceGUI page stays the same either way — only the Marimo server location changes.

## Open Questions
- Auth: how to pass NiceGUI user identity to Marimo sessions?
- Notebook management: predefined notebooks or user-created?
- Resource limits: should backtests have CPU/memory caps?
- State persistence: save notebook state between sessions?
