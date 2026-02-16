from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from kitsune.agents.tools.notebook import with_notebooks
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
        "You are Kitsune, an AI data analysis assistant. "
        "You can create and run marimo notebooks for interactive data analysis. "
        "When asked to analyze data or create visualizations, write a marimo notebook "
        "using the write_notebook tool, then run it with run_notebook to verify it works."
    ),
)

with_notebooks(agent)


def create_deps() -> MarimoAgentDeps:
    return MarimoAgentDeps()


def create_agent() -> Agent[MarimoAgentDeps]:
    return agent
