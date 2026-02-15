from nicegui import ui

from kitsune.agent import agent, deps
from kitsune.ui.layout import frame

CHAT_CSS = """
.kitsune-chat-area {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 1rem;
}

.kitsune-msg {
    display: flex;
    gap: 10px;
    max-width: 80%;
    animation: msg-in 0.2s ease-out;
}
@keyframes msg-in {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
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

.kitsune-input-bar {
    background: var(--kitsune-surface, #1a1b26) !important;
    border-top: 1px solid var(--kitsune-border, #2f3146) !important;
    backdrop-filter: blur(12px);
    padding: 12px 0 !important;
}
"""


def setup() -> None:
    @ui.page("/")
    async def chat_page():
        ui.add_head_html(f"<style>{CHAT_CSS}</style>")
        messages: list[dict[str, str]] = []

        @ui.refreshable
        def chat_messages():
            for msg in messages:
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
                        ui.markdown(msg["text"])

            # Auto-scroll anchor
            ui.element("div").props('id="scroll-anchor"')
            ui.run_javascript(
                'document.getElementById("scroll-anchor")?.scrollIntoView({behavior:"smooth"})'
            )

        async def send(_) -> None:
            question = text_input.value
            if not question or not question.strip():
                return
            text_input.value = ""

            messages.append({"role": "user", "text": question})
            messages.append({"role": "assistant", "text": ""})
            chat_messages.refresh()

            async with agent.run_stream(question, deps=deps) as result:
                async for chunk in result.stream_text(delta=True):
                    messages[-1]["text"] += chunk
                    chat_messages.refresh()

        with frame("Kitsune — Chat"):
            with ui.column().classes("kitsune-chat-area w-full"):
                chat_messages()

        with ui.footer().classes("kitsune-input-bar"):
            with ui.row().classes(
                "w-full max-w-3xl mx-auto items-center gap-2 px-2"
            ):
                text_input = (
                    ui.input(placeholder="Type a message...")
                    .classes("flex-grow")
                    .on("keydown.enter", send)
                    .props("outlined rounded dense dark")
                )
                ui.button(
                    icon="send",
                    on_click=lambda: send(None),
                ).props("round flat color=purple-4 size=md")
