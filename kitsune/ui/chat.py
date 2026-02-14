from nicegui import ui

from kitsune.agent import agent, deps
from kitsune.ui.layout import frame


def setup() -> None:
    @ui.page("/")
    async def chat_page():
        messages: list[dict[str, str]] = []

        @ui.refreshable
        def chat_messages():
            for msg in messages:
                with ui.chat_message(
                    name=msg["role"],
                    sent=msg["role"] == "user",
                ):
                    ui.markdown(msg["text"])

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
            chat_messages()

        with ui.footer():
            with ui.row().classes("w-full max-w-3xl mx-auto"):
                text_input = (
                    ui.input(placeholder="Type a message...")
                    .classes("flex-grow")
                    .on("keydown.enter", send)
                    .props("outlined rounded")
                )
