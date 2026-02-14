import logfire
from pydantic_ai import Agent

from kitsune.models import Deps, MemoryStore

logfire.configure()
logfire.instrument_pydantic_ai()

memory = MemoryStore()
deps = Deps(memory=memory)

agent = Agent(
    "openrouter:moonshotai/kimi-k2.5",
    deps_type=Deps,
    instructions=(
        "You are Kitsune, a personal AI assistant with persistent memory."
    ),
)
