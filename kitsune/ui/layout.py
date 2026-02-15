from contextlib import contextmanager

from nicegui import ui

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --kitsune-bg: #0f1117;
    --kitsune-surface: #1a1b26;
    --kitsune-surface-hover: #24253a;
    --kitsune-border: #2f3146;
    --kitsune-text: #e1e2e8;
    --kitsune-text-muted: #8b8fa3;
    --kitsune-accent: #7c6af6;
    --kitsune-accent-hover: #9182f7;
}

body {
    font-family: 'Inter', sans-serif !important;
    background: var(--kitsune-bg) !important;
}

.q-header {
    background: linear-gradient(135deg, #1a1b26 0%, #252640 100%) !important;
    border-bottom: 1px solid var(--kitsune-border) !important;
    box-shadow: 0 1px 8px rgba(0,0,0,0.3) !important;
}

.q-drawer {
    background: var(--kitsune-surface) !important;
    border-right: 1px solid var(--kitsune-border) !important;
}

.kitsune-nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    margin: 2px 8px;
    border-radius: 8px;
    color: var(--kitsune-text-muted);
    text-decoration: none !important;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.15s ease;
}
.kitsune-nav-link:hover {
    background: var(--kitsune-surface-hover);
    color: var(--kitsune-text);
}
.kitsune-nav-link.active {
    background: rgba(124,106,246,0.12);
    color: var(--kitsune-accent);
}

.kitsune-nav-icon {
    font-size: 1.25rem;
    width: 24px;
    text-align: center;
}

.q-footer {
    background: var(--kitsune-surface) !important;
    border-top: 1px solid var(--kitsune-border) !important;
}

.q-field--outlined .q-field__control {
    background: var(--kitsune-surface) !important;
    border-color: var(--kitsune-border) !important;
    color: var(--kitsune-text) !important;
}
.q-field--outlined .q-field__control:hover {
    border-color: var(--kitsune-accent) !important;
}
.q-field__native, .q-field__input {
    color: var(--kitsune-text) !important;
}
.q-field__label {
    color: var(--kitsune-text-muted) !important;
}

/* Scrollbar styling */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--kitsune-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--kitsune-text-muted); }
"""

NAV_ITEMS = [
    {"label": "Chat", "icon": "chat_bubble_outline", "path": "/"},
    {"label": "Dashboard", "icon": "dashboard", "path": "/dashboard"},
    {"label": "Notebooks", "icon": "menu_book", "path": "/notebooks"},
]


@contextmanager
def frame(title: str = "Kitsune"):
    ui.add_head_html(f"<style>{CUSTOM_CSS}</style>")

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

        # Highlight the active nav link via JS (works reliably across pages)
        ui.run_javascript("""
            document.querySelectorAll('.kitsune-nav-link').forEach(link => {
                if (link.getAttribute('href') === window.location.pathname) {
                    link.classList.add('active');
                }
            });
        """)

    with ui.column().classes("w-full max-w-3xl mx-auto p-4"):
        yield
