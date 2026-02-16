from __future__ import annotations

from typing import Literal

import httpx
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from kitsune.config import get_config


class LinkupSource(BaseModel):
	url: str = Field(description="The URL of the source.")
	name: str = Field(description="The title of the source page.")
	snippet: str = Field(description="A brief snippet from the source.")


class LinkupSearchResult(BaseModel):
	answer: str = Field(
		description="The generated answer based on the search results.",
	)
	sources: list[LinkupSource] = Field(description="List of search results.")


class LinkupFetchResult(BaseModel):
	markdown: str = Field(
		description="The content of the fetched webpage in markdown format.",
	)


async def _linkup_post(endpoint: str, payload: dict) -> dict:
	config = get_config()
	url = f"{config.LINKUP_URL}/{endpoint}"
	headers = {
		"Authorization": f"Bearer {config.LINKUP_API_KEY}",
		"Content-Type": "application/json",
	}

	async with httpx.AsyncClient() as client:
		response = await client.post(url, headers=headers, json=payload)

	if response.is_error:
		raise RuntimeError(
			f"LinkUp API error: {response.status_code} {response.reason_phrase}",
		)

	return response.json()


async def search_linkup(
	query: str,
	depth: Literal["standard", "deep"],
) -> LinkupSearchResult:
	data = await _linkup_post(
		endpoint="search",
		payload={
			"q": query,
			"depth": depth,
			"outputType": "sourcedAnswer",
			"includeImages": False,
			"includeInlineCitations": False,
		},
	)
	return LinkupSearchResult.model_validate(data)


async def fetch_linkup(
	url: str,
	render_js: bool = False,
) -> LinkupFetchResult:
	data = await _linkup_post(
		endpoint="fetch",
		payload={
			"url": url,
			"includeRawHtml": False,
			"renderJs": render_js,
			"extractImages": False,
		},
	)
	return LinkupFetchResult.model_validate(data)


def with_linkup(agent: Agent) -> Agent:
    @agent.tool
    async def search_tool(_: RunContext, query: str, depth: Literal["standard", "deep"] = "standard") -> LinkupSearchResult:
        return await search_linkup(query, depth)
	
    @agent.tool
    async def fetch_tool(_: RunContext, url: str, render_js: bool = False) -> LinkupFetchResult:
        return await fetch_linkup(url, render_js)

    return agent
