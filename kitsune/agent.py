from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from kitsune.config import get_config
from kitsune.models import Deps, MemoryStore

config = get_config()

memory = MemoryStore()
deps = Deps(memory=memory)

model = OpenAIChatModel(
    provider=OpenAIProvider(base_url=config.LOCAL_URL),
    model_name=config.LOCAL_MODEL,
)

agent = Agent(
    model=model,
    deps_type=Deps,
    instructions=(
        "You are Kitsune, a personal AI assistant with persistent memory."
    ),
)
