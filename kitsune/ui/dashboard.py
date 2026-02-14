from nicegui import ui

from kitsune.ui.layout import frame


def setup() -> None:
    @ui.page("/dashboard")
    def dashboard_page():
        with frame("Kitsune — Dashboard"):
            ui.label("Dashboard coming soon.").classes("text-h5 text-gray-500")
