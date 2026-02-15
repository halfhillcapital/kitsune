from nicegui import ui

from kitsune.ui.layout import frame


def setup() -> None:
    @ui.page("/notebooks")
    def notebooks_page():
        with frame("Kitsune — Notebooks"):
            with ui.column().classes("items-center justify-center w-full py-20 gap-4"):
                ui.icon("menu_book", size="4rem").style(
                    "color: var(--kitsune-text-muted, #8b8fa3); opacity: 0.5;"
                )
                ui.label("Notebooks").classes("text-h5 font-semibold").style(
                    "color: var(--kitsune-text, #e1e2e8);"
                )
                ui.label(
                    "Interactive Marimo notebooks will be embedded here."
                ).style(
                    "color: var(--kitsune-text-muted, #8b8fa3); font-size: 0.95rem;"
                )
