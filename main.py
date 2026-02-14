from nicegui import ui

from kitsune.ui import chat, dashboard, notebooks

chat.setup()
dashboard.setup()
notebooks.setup()

ui.run(port=8010, reload=True, title="Kitsune")
