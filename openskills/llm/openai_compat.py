"""
OpenAI-compatible LLM client.

Works with OpenAI, Claude (via proxy), and other compatible APIs.
Supports multimodal messages (text + images).
"""

import json
import os
from typing import AsyncIterator

import httpx

from openskills.llm.base import (
    BaseLLMClient,
    Message,
    ChatResponse,
    StreamChunk,
    ToolCall,
    ImageContent,
)


class OpenAICompatClient(BaseLLMClient):
    """
    OpenAI-compatible API client.

    Supports any API that follows the OpenAI chat completions format,
    including:
    - OpenAI (gpt-4, gpt-4-vision, gpt-3.5-turbo, etc.)
    - Anthropic Claude (via openai-compatible proxy)
    - Local models (Ollama, LM Studio, etc.)
    - Azure OpenAI

    Features:
    - Multimodal support (text + images)
    - Streaming responses
    - Tool/function calling
    - Configurable timeouts and retries
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4",
        default_headers: dict | None = None,
        timeout: float = 120.0,
        max_retries: int = 2,
    ):
        """
        Initialize the client.

        Args:
            api_key: API key (defaults to OPENAI_API_KEY env var)
            base_url: Base URL for the API (defaults to OpenAI)
            model: Default model to use
            default_headers: Additional headers to include
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "")).rstrip("/")
        if not self.base_url:
            self.base_url = "https://api.openai.com/v1"
        self.model = model
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> ChatResponse:
        """
        Send a chat completion request.

        Args:
            messages: List of chat messages (can include images)
            system: Optional system prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            model: Model to use (overrides default)
            tools: List of tool definitions for function calling
            tool_choice: Tool choice strategy ("auto", "none", or specific tool)
            **kwargs: Additional API parameters

        Returns:
            ChatResponse with the completion
        """
        request_messages = self._prepare_messages(messages, system)

        payload = {
            "model": model or self.model,
            "messages": request_messages,
            "temperature": temperature,
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        response = await self._make_request(payload)
        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        # Parse tool calls if present
        tool_calls = []
        if "tool_calls" in message:
            for tc in message["tool_calls"]:
                tool_calls.append(ToolCall(
                    id=tc["id"],
                    name=tc["function"]["name"],
                    arguments=tc["function"]["arguments"],
                ))

        return ChatResponse(
            content=message.get("content", "") or "",
            model=data.get("model", ""),
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason", ""),
            tool_calls=tool_calls,
        )

    async def chat_stream(
        self,
        messages: list[Message],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """
        Send a streaming chat completion request.

        Args:
            messages: List of chat messages (can include images)
            system: Optional system prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            model: Model to use (overrides default)
            tools: List of tool definitions for function calling
            tool_choice: Tool choice strategy
            **kwargs: Additional API parameters

        Yields:
            StreamChunk objects as they arrive
        """
        request_messages = self._prepare_messages(messages, system)

        payload = {
            "model": model or self.model,
            "messages": request_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        async with self._client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._get_headers(),
            json=payload,
        ) as response:
            response.raise_for_status()

            # Track tool call accumulation for streaming
            current_tool_calls: dict[int, dict] = {}

            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue

                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                    choice = data["choices"][0]
                    delta = choice.get("delta", {})
                    finish_reason = choice.get("finish_reason")

                    # Handle content
                    content = delta.get("content", "")

                    # Handle tool calls (streaming)
                    tool_calls = []
                    if "tool_calls" in delta:
                        for tc in delta["tool_calls"]:
                            idx = tc.get("index", 0)
                            if idx not in current_tool_calls:
                                current_tool_calls[idx] = {
                                    "id": tc.get("id", ""),
                                    "name": "",
                                    "arguments": "",
                                }
                            if "id" in tc:
                                current_tool_calls[idx]["id"] = tc["id"]
                            if "function" in tc:
                                if "name" in tc["function"]:
                                    current_tool_calls[idx]["name"] = tc["function"]["name"]
                                if "arguments" in tc["function"]:
                                    current_tool_calls[idx]["arguments"] += tc["function"]["arguments"]

                    # On finish, return accumulated tool calls
                    if finish_reason and current_tool_calls:
                        tool_calls = [
                            ToolCall(
                                id=tc["id"],
                                name=tc["name"],
                                arguments=tc["arguments"],
                            )
                            for tc in current_tool_calls.values()
                        ]

                    yield StreamChunk(
                        content=content,
                        finish_reason=finish_reason,
                        tool_calls=tool_calls,
                    )

                except json.JSONDecodeError:
                    continue

    async def _make_request(
        self,
        payload: dict,
        retries: int = 0,
    ) -> httpx.Response:
        """Make an API request with retry logic."""
        try:
            response = await self._client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            # Retry on 5xx errors or rate limits
            if e.response.status_code >= 500 or e.response.status_code == 429:
                if retries < self.max_retries:
                    import asyncio
                    await asyncio.sleep(2 ** retries)  # Exponential backoff
                    return await self._make_request(payload, retries + 1)
            raise

        except httpx.RequestError:
            if retries < self.max_retries:
                import asyncio
                await asyncio.sleep(2 ** retries)
                return await self._make_request(payload, retries + 1)
            raise

    def _prepare_messages(
        self,
        messages: list[Message],
        system: str | None,
    ) -> list[dict]:
        """Prepare messages for the API request."""
        result = []

        if system:
            result.append({"role": "system", "content": system})

        for msg in messages:
            # Use the message's to_dict method for proper multimodal support
            result.append(msg.to_dict())

        return result

    def _get_headers(self) -> dict:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            **self.default_headers,
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


class AzureOpenAIClient(OpenAICompatClient):
    """
    Azure OpenAI API client.

    Azure OpenAI has a different API format:
    - Endpoint: https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions
    - Auth: api-key header instead of Bearer token
    - Requires api-version parameter

    Environment variables:
    - AZURE_OPENAI_API_KEY: API key
    - AZURE_OPENAI_ENDPOINT: Resource endpoint (e.g., https://myresource.openai.azure.com)
    - AZURE_OPENAI_API_VERSION: API version (default: 2024-02-15-preview)
    """

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        deployment: str | None = None,
        api_version: str | None = None,
        default_headers: dict | None = None,
        timeout: float = 120.0,
        max_retries: int = 2,
    ):
        """
        Initialize Azure OpenAI client.

        Args:
            api_key: Azure OpenAI API key (defaults to AZURE_OPENAI_API_KEY)
            endpoint: Azure OpenAI endpoint (defaults to AZURE_OPENAI_ENDPOINT)
            deployment: Deployment name (defaults to AZURE_OPENAI_DEPLOYMENT)
            api_version: API version (defaults to AZURE_OPENAI_API_VERSION or 2024-02-15-preview)
            default_headers: Additional headers
            timeout: Request timeout
            max_retries: Max retries
        """
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY", "")
        self.endpoint = (endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")).rstrip("/")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.max_retries = max_retries

        # For compatibility with parent class
        self.model = self.deployment
        self.base_url = self.endpoint

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    def _get_chat_url(self) -> str:
        """Get the Azure chat completions URL."""
        return f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"

    def _get_headers(self) -> dict:
        """Get request headers for Azure."""
        headers = {
            "Content-Type": "application/json",
            **self.default_headers,
        }
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers

    async def _make_request(
        self,
        payload: dict,
        retries: int = 0,
    ) -> httpx.Response:
        """Make an API request to Azure OpenAI."""
        # Remove model from payload - Azure uses deployment in URL
        payload = {k: v for k, v in payload.items() if k != "model"}

        try:
            response = await self._client.post(
                self._get_chat_url(),
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500 or e.response.status_code == 429:
                if retries < self.max_retries:
                    import asyncio
                    await asyncio.sleep(2 ** retries)
                    return await self._make_request(payload, retries + 1)
            raise

        except httpx.RequestError:
            if retries < self.max_retries:
                import asyncio
                await asyncio.sleep(2 ** retries)
                return await self._make_request(payload, retries + 1)
            raise

    async def chat_stream(
        self,
        messages: list[Message],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request to Azure OpenAI."""
        request_messages = self._prepare_messages(messages, system)

        payload = {
            "messages": request_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        async with self._client.stream(
            "POST",
            self._get_chat_url(),
            headers=self._get_headers(),
            json=payload,
        ) as response:
            response.raise_for_status()

            current_tool_calls: dict[int, dict] = {}

            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue

                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                    choice = data["choices"][0]
                    delta = choice.get("delta", {})
                    finish_reason = choice.get("finish_reason")

                    content = delta.get("content", "")

                    tool_calls = []
                    if "tool_calls" in delta:
                        for tc in delta["tool_calls"]:
                            idx = tc.get("index", 0)
                            if idx not in current_tool_calls:
                                current_tool_calls[idx] = {
                                    "id": tc.get("id", ""),
                                    "name": "",
                                    "arguments": "",
                                }
                            if "id" in tc:
                                current_tool_calls[idx]["id"] = tc["id"]
                            if "function" in tc:
                                if "name" in tc["function"]:
                                    current_tool_calls[idx]["name"] = tc["function"]["name"]
                                if "arguments" in tc["function"]:
                                    current_tool_calls[idx]["arguments"] += tc["function"]["arguments"]

                    if finish_reason and current_tool_calls:
                        tool_calls = [
                            ToolCall(
                                id=tc["id"],
                                name=tc["name"],
                                arguments=tc["arguments"],
                            )
                            for tc in current_tool_calls.values()
                        ]

                    yield StreamChunk(
                        content=content,
                        finish_reason=finish_reason,
                        tool_calls=tool_calls,
                    )

                except json.JSONDecodeError:
                    continue


# Convenience function to create a client
def create_client(
    provider: str = "openai",
    api_key: str | None = None,
    model: str | None = None,
    **kwargs,
) -> OpenAICompatClient:
    """
    Create an LLM client for a specific provider.

    Args:
        provider: Provider name ("openai", "azure", "ollama", "together", etc.)
        api_key: API key (uses environment variable if not provided)
        model: Model to use (uses provider default if not provided)
        **kwargs: Additional client options

    Returns:
        Configured OpenAICompatClient or AzureOpenAIClient

    Examples:
        # OpenAI
        client = create_client("openai", model="gpt-4-turbo")

        # Azure OpenAI
        client = create_client("azure", deployment="my-gpt4-deployment")

        # Ollama (local)
        client = create_client("ollama", model="llama2")

        # Together AI
        client = create_client("together", model="mistralai/Mixtral-8x7B-Instruct-v0.1")
    """
    # Special handling for Azure
    if provider == "azure":
        return AzureOpenAIClient(
            api_key=api_key,
            endpoint=kwargs.pop("endpoint", None),
            deployment=kwargs.pop("deployment", model),
            api_version=kwargs.pop("api_version", None),
            **kwargs,
        )

    provider_configs = {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_API_KEY",
            "default_model": "gpt-4",
        },
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "api_key_env": None,
            "default_model": "llama2",
        },
        "together": {
            "base_url": "https://api.together.xyz/v1",
            "api_key_env": "TOGETHER_API_KEY",
            "default_model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "api_key_env": "GROQ_API_KEY",
            "default_model": "mixtral-8x7b-32768",
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "api_key_env": "DEEPSEEK_API_KEY",
            "default_model": "deepseek-chat",
        },
    }

    config = provider_configs.get(provider, {})

    # Get API key
    if not api_key and config.get("api_key_env"):
        api_key = os.getenv(config["api_key_env"], "")

    # Get base URL
    base_url = kwargs.pop("base_url", None) or config.get("base_url")

    # Get model
    if not model:
        model = config.get("default_model", "gpt-4")

    return OpenAICompatClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        **kwargs,
    )
