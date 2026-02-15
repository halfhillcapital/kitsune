import logfire
from nicegui import app, ui

from kitsune.ui import chat, dashboard, notebooks

logfire.configure()
logfire.instrument_pydantic_ai()

app.on_startup(lambda: ui.colors(primary="#7c6af6"))

app.add_static_files("/static", "kitsune/ui/static")

chat.setup()
dashboard.setup()
notebooks.setup()

ui.run(port=8010, reload=True, title="Kitsune", dark=True)
