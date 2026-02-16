from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from kitsune.config import get_config

config = get_config()

@dataclass
class MarimoAgentDeps:
    pass

model = OpenAIChatModel(
    provider=OpenAIProvider(base_url=config.LOCAL_URL),
    model_name=config.LOCAL_MODEL,
)

agent = Agent(
    model=model,
    deps_type=MarimoAgentDeps,
    instructions=(
        "You are Kitsune, a personal AI assistant with persistent memory."
    ),
)

def create_deps() -> MarimoAgentDeps:
    return MarimoAgentDeps()

def create_agent() -> Agent[MarimoAgentDeps]:
    return agent
