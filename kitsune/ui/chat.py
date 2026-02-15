import logging
from typing import Required, TypedDict

from nicegui import ui

from kitsune.agent import agent, deps
from kitsune.ui.layout import frame

logger = logging.getLogger(__name__)


class Message(TypedDict, total=False):
    role: Required[str]
    text: Required[str]
    error: bool


def setup() -> None:
    @ui.page("/")
    async def chat_page():
        ui.add_head_html('<link rel="stylesheet" href="/static/chat.css">')
        ui.run_javascript("document.body.classList.add('kitsune-chat-page')")
        messages: list[Message] = []
        # Holds a reference to the last assistant markdown element for streaming updates
        last_md_ref: list[ui.markdown | None] = [None]

        def _scroll_down():
            try:
                ui.run_javascript(
                    'document.getElementById("scroll-anchor")'
                    '?.scrollIntoView({behavior:"smooth"})'
                )
            except Exception:
                logger.debug("scroll failed", exc_info=True)

        def _render_message(msg: Message) -> ui.markdown | None:
            """Render a single message bubble, return the markdown element."""
            role = msg["role"]
            is_user = role == "user"
            is_error = msg.get("error")
            side = "user" if is_user else "assistant"

            with ui.row().classes(
                f"kitsune-msg-{side} w-full mb-3 flex gap-2.5"
                + (" ml-auto flex-row-reverse" if is_user else " mr-auto")
            ):
                with ui.element("div").classes(
                    f"kitsune-avatar-{side} w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0 mt-0.5"
                ):
                    ui.icon(
                        "person" if is_user else "auto_awesome", size="xs"
                    )
                if is_error:
                    with ui.element("div").classes("kitsune-error-bubble"):
                        ui.label("Something went wrong. Please try again.")
                    return None
                elif not is_user and not msg["text"]:
                    # Typing indicator while waiting for first chunk
                    with ui.element("div").classes(
                        f"kitsune-bubble kitsune-bubble-{side} px-4 py-3 rounded-2xl text-sm leading-relaxed break-words"
                    ).style("padding: 14px 20px;"):
                        with ui.row().classes("items-center gap-0"):
                            for _ in range(3):
                                ui.element("span").classes("kitsune-typing-dot")
                    return None
                else:
                    with ui.element("div").classes(
                        f"kitsune-bubble kitsune-bubble-{side} px-4 py-3 rounded-2xl text-sm leading-relaxed break-words"
                    ):
                        md = ui.markdown(msg["text"])
                    return md

        async def send(_) -> None:
            active_input = bottom_input if messages else welcome_input
            question = active_input.value
            if not question or not question.strip():
                return
            active_input.value = ""

            messages.append({"role": "user", "text": question})
            messages.append({"role": "assistant", "text": ""})
            # Switch from welcome screen to chat view (hide/show, no destroy)
            welcome_section.set_visibility(False)
            chat_section.set_visibility(True)
            chat_area.refresh()
            bottom_row.set_visibility(True)
            bottom_input.run_method("focus")

            try:
                async with agent.run_stream(question, deps=deps) as result:
                    async for chunk in result.stream_text(delta=True):
                        messages[-1]["text"] += chunk
                        if last_md_ref[0] is None:
                            # First chunk arrived — replace typing indicator with markdown
                            chat_area.refresh()
                        if last_md_ref[0] is not None:
                            last_md_ref[0].set_content(messages[-1]["text"])
                            _scroll_down()
            except Exception:
                logger.exception("agent stream failed")
                messages[-1]["text"] = ""
                messages[-1]["error"] = True
                chat_area.refresh()

        @ui.refreshable
        def chat_area():
            with ui.element("div").classes("kitsune-chat-area flex-1 overflow-y-auto py-4"):
                last_md_ref[0] = None
                for i, msg in enumerate(messages):
                    result = _render_message(msg)
                    # Only track the markdown for the final message (the one being streamed)
                    if result is not None and i == len(messages) - 1 and msg["role"] == "assistant":
                        last_md_ref[0] = result
                ui.element("div").props('id="scroll-anchor"')
            _scroll_down()

        with frame("Kitsune — Chat") as content:
            content.classes("kitsune-chat-container-wrapper")
            with ui.element("div").classes(
                "flex flex-col h-[calc(100vh-64px)] max-w-3xl mx-auto w-full px-4 pt-4 overflow-hidden"
            ):
                # Welcome section — visible until first message, then hidden (never destroyed)
                welcome_section = ui.element("div").classes(
                    "flex-1 flex flex-col items-center justify-center gap-6"
                )
                welcome_section.set_visibility(not messages)
                with welcome_section:
                    ui.icon("auto_awesome", size="3rem").classes(
                        "kitsune-welcome-icon"
                    )
                    ui.label("What can I help you with?").classes(
                        "kitsune-welcome-text"
                    )
                    with ui.row().classes("py-3 pb-5 w-full shrink-0 items-center"):
                        welcome_input = (
                            ui.input(placeholder="Type a message...")
                            .classes("flex-grow")
                            .on("keydown.enter", send)
                            .props("outlined rounded dense dark autofocus")
                        )

                # Chat section — hidden until first message
                chat_section = ui.element("div").classes("flex-1 flex flex-col overflow-hidden")
                chat_section.set_visibility(bool(messages))
                with chat_section:
                    chat_area()

                bottom_row = ui.row().classes("py-3 pb-5 w-full shrink-0 items-center")
                bottom_row.set_visibility(bool(messages))
                with bottom_row:
                    bottom_input = (
                        ui.input(placeholder="Type a message...")
                        .classes("flex-grow")
                        .on("keydown.enter", send)
                        .props("outlined rounded dense dark")
                    )
