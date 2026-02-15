from nicegui import app, ui

from kitsune.ui import chat, dashboard, notebooks

app.on_startup(lambda: ui.colors(primary="#7c6af6"))

chat.setup()
dashboard.setup()
notebooks.setup()

ui.run(port=8010, reload=True, title="Kitsune", dark=True)
