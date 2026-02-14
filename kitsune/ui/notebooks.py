from nicegui import ui

from kitsune.ui.layout import frame


def setup() -> None:
    @ui.page("/notebooks")
    def notebooks_page():
        with frame("Kitsune — Notebooks"):
            ui.label("Marimo notebook embedding coming soon.").classes(
                "text-h5 text-gray-500"
            )
            ui.markdown(
                "This page will host interactive Marimo notebooks "
                "mounted via ASGI into the NiceGUI app."
            )
