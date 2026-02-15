from nicegui import ui

from kitsune.agent import agent, deps
from kitsune.ui.layout import frame

CHAT_CSS = """
.kitsune-chat-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 64px);
    max-width: 48rem;
    margin: 0 auto;
    width: 100%;
    padding: 0 1rem;
    overflow: hidden;
}

/* Remove frame wrapper padding so chat fills viewport exactly */
.kitsune-chat-container-wrapper {
    padding: 0 !important;
    max-width: 100% !important;
    height: calc(100vh - 64px);
    overflow: hidden;
}

/* Prevent all Quasar/NiceGUI ancestors from scrolling on chat page */
.q-layout, .q-page-container, .q-page, .nicegui-content {
    overflow: hidden !important;
    min-height: 0 !important;
}
html, body {
    overflow: hidden !important;
}

/* Empty state: center the welcome content */
.kitsune-empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
}

/* Messages area: scrollable, fills available space */
.kitsune-chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 0;
    scrollbar-width: none;
    -ms-overflow-style: none;
}
.kitsune-chat-area::-webkit-scrollbar {
    display: none;
}

/* Input always pinned at bottom */
.kitsune-input-row {
    padding: 12px 0 20px;
    width: 100%;
    flex-shrink: 0;
}

.kitsune-msg {
    display: flex;
    gap: 10px;
    max-width: 80%;
}
.kitsune-msg-user { margin-left: auto; flex-direction: row-reverse; }
.kitsune-msg-assistant { margin-right: auto; }

.kitsune-bubble {
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 0.9rem;
    line-height: 1.55;
    word-break: break-word;
}
.kitsune-bubble-user {
    background: linear-gradient(135deg, #7c6af6, #6355d8);
    color: #fff;
    border-bottom-right-radius: 4px;
}
.kitsune-bubble-assistant {
    background: var(--kitsune-surface-hover, #24253a);
    color: var(--kitsune-text, #e1e2e8);
    border: 1px solid var(--kitsune-border, #2f3146);
    border-bottom-left-radius: 4px;
}

.kitsune-bubble p { margin: 0 0 0.5em; }
.kitsune-bubble p:last-child { margin-bottom: 0; }
.kitsune-bubble code {
    background: rgba(0,0,0,0.25);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
}
.kitsune-bubble pre {
    background: rgba(0,0,0,0.3);
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;
}

.kitsune-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.kitsune-avatar-user { background: #7c6af6; color: #fff; }
.kitsune-avatar-assistant { background: var(--kitsune-surface-hover, #24253a); color: #a78bfa; border: 1px solid var(--kitsune-border, #2f3146); }

.kitsune-welcome-icon {
    opacity: 0.4;
    color: var(--kitsune-text-muted, #8b8fa3);
}
.kitsune-welcome-text {
    color: var(--kitsune-text-muted, #8b8fa3);
    font-size: 1.1rem;
    font-weight: 500;
}
"""


def setup() -> None:
    @ui.page("/")
    async def chat_page():
        ui.add_head_html(f"<style>{CHAT_CSS}</style>")
        messages: list[dict[str, str]] = []
        # Holds a reference to the last assistant markdown element for streaming updates
        last_md_ref: list[ui.markdown | None] = [None]

        def _scroll_down():
            try:
                ui.run_javascript(
                    'document.getElementById("scroll-anchor")'
                    '?.scrollIntoView({behavior:"smooth"})'
                )
            except Exception:
                pass

        def _render_message(msg: dict[str, str]) -> ui.markdown:
            """Render a single message bubble, return the markdown element."""
            role = msg["role"]
            is_user = role == "user"
            side = "user" if is_user else "assistant"

            with ui.row().classes(f"kitsune-msg kitsune-msg-{side} w-full mb-3"):
                with ui.element("div").classes(
                    f"kitsune-avatar kitsune-avatar-{side}"
                ):
                    ui.icon(
                        "person" if is_user else "auto_awesome", size="xs"
                    )
                with ui.element("div").classes(
                    f"kitsune-bubble kitsune-bubble-{side}"
                ):
                    md = ui.markdown(msg["text"])
            return md

        async def send(_) -> None:
            # Read from whichever input is currently visible
            active_input = bottom_input if messages else welcome_input
            question = active_input.value
            if not question or not question.strip():
                return
            active_input.value = ""

            messages.append({"role": "user", "text": question})
            messages.append({"role": "assistant", "text": ""})
            chat_area.refresh()
            bottom_row.set_visibility(True)

            async with agent.run_stream(question, deps=deps) as result:
                async for chunk in result.stream_text(delta=True):
                    messages[-1]["text"] += chunk
                    if last_md_ref[0] is not None:
                        last_md_ref[0].set_content(messages[-1]["text"])
                        try:
                            _scroll_down()
                        except Exception:
                            pass

        @ui.refreshable
        def chat_area():
            if not messages:
                with ui.element("div").classes("kitsune-empty-state"):
                    ui.icon("auto_awesome", size="3rem").classes(
                        "kitsune-welcome-icon"
                    )
                    ui.label("What can I help you with?").classes(
                        "kitsune-welcome-text"
                    )
                    with ui.row().classes("kitsune-input-row items-center w-full"):
                        nonlocal welcome_input
                        welcome_input = (
                            ui.input(placeholder="Type a message...")
                            .classes("flex-grow")
                            .on("keydown.enter", send)
                            .props("outlined rounded dense dark")
                        )
            else:
                with ui.element("div").classes("kitsune-chat-area"):
                    for msg in messages:
                        md = _render_message(msg)
                    if messages[-1]["role"] == "assistant":
                        last_md_ref[0] = md
                    ui.element("div").props('id="scroll-anchor"')
                _scroll_down()

        welcome_input: ui.input = None  # type: ignore[assignment]

        with frame("Kitsune — Chat") as content:
            content.classes("kitsune-chat-container-wrapper")
            with ui.element("div").classes("kitsune-chat-container"):
                chat_area()

                bottom_row = ui.row().classes("kitsune-input-row items-center w-full")
                bottom_row.set_visibility(bool(messages))
                with bottom_row:
                    bottom_input = (
                        ui.input(placeholder="Type a message...")
                        .classes("flex-grow")
                        .on("keydown.enter", send)
                        .props("outlined rounded dense dark")
                    )
