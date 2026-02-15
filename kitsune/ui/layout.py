from contextlib import contextmanager

from nicegui import ui

NAV_ITEMS = [
    {"label": "Chat", "icon": "chat_bubble_outline", "path": "/"},
    {"label": "Dashboard", "icon": "dashboard", "path": "/dashboard"},
    {"label": "Notebooks", "icon": "menu_book", "path": "/notebooks"},
]


@contextmanager
def frame(title: str = "Kitsune"):
    ui.add_head_html('<link rel="stylesheet" href="/static/layout.css">')

    with ui.header().classes("items-center justify-between px-4"):
        ui.button(on_click=lambda: drawer.toggle(), icon="menu").props(
            "flat color=white round size=sm"
        )
        with ui.row().classes("items-center gap-2 no-wrap"):
            ui.icon("auto_awesome", size="sm").classes("text-purple-300")
            ui.label(title).classes("text-subtitle1 font-medium tracking-wide")

    with ui.left_drawer(value=True, bordered=False).classes("p-0") as drawer:
        with ui.column().classes("w-full pt-4 gap-0"):
            for item in NAV_ITEMS:
                with ui.link(target=item["path"]).classes(
                    "kitsune-nav-link"
                ).style("text-decoration: none"):
                    ui.icon(item["icon"]).classes("kitsune-nav-icon")
                    ui.label(item["label"])

        # Highlight the active nav link via JS (setTimeout ensures DOM is ready)
        ui.run_javascript("""
            setTimeout(() => {
                document.querySelectorAll('.kitsune-nav-link').forEach(link => {
                    if (link.getAttribute('href') === window.location.pathname) {
                        link.classList.add('active');
                    }
                });
            }, 50);
        """)

    with ui.column().classes("w-full max-w-3xl mx-auto p-4") as content:
        yield content
