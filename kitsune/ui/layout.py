from contextlib import contextmanager

from nicegui import ui


@contextmanager
def frame(title: str = "Kitsune"):
    with ui.header().classes("items-center justify-between"):
        ui.button(on_click=lambda: drawer.toggle(), icon="menu").props(
            "flat color=white"
        )
        ui.label(title).classes("text-h6")

    with ui.left_drawer(value=True, bordered=True) as drawer:
        ui.link("Chat", "/").classes("text-lg p-2")
        ui.link("Dashboard", "/dashboard").classes("text-lg p-2")
        ui.link("Notebooks", "/notebooks").classes("text-lg p-2")

    with ui.column().classes("w-full max-w-3xl mx-auto p-4"):
        yield
