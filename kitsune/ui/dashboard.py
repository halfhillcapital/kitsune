from nicegui import ui

from kitsune.ui.layout import frame


def setup() -> None:
    @ui.page("/dashboard")
    def dashboard_page():
        with frame("Kitsune — Dashboard"):
            with ui.column().classes("items-center justify-center w-full py-20 gap-4"):
                ui.icon("dashboard", size="4rem").style(
                    "color: var(--kitsune-text-muted, #8b8fa3); opacity: 0.5;"
                )
                ui.label("Dashboard").classes("text-h5 font-semibold").style(
                    "color: var(--kitsune-text, #e1e2e8);"
                )
                ui.label("Analytics and insights coming soon.").style(
                    "color: var(--kitsune-text-muted, #8b8fa3); font-size: 0.95rem;"
                )
