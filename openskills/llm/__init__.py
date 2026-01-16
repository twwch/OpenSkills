"""LLM integration for OpenSkills."""

from openskills.llm.base import (
    BaseLLMClient,
    Message,
    ChatResponse,
    StreamChunk,
    ToolCall,
    ImageContent,
    TextContent,
    ImageDetail,
    image_url,
    image_file,
    image_base64,
    text,
)
from openskills.llm.openai_compat import OpenAICompatClient, AzureOpenAIClient, create_client
from openskills.llm.prompt_builder import PromptBuilder

__all__ = [
    # Base classes
    "BaseLLMClient",
    "Message",
    "ChatResponse",
    "StreamChunk",
    "ToolCall",
    # Multimodal content
    "ImageContent",
    "TextContent",
    "ImageDetail",
    # Content helpers
    "image_url",
    "image_file",
    "image_base64",
    "text",
    # Clients
    "OpenAICompatClient",
    "AzureOpenAIClient",
    "create_client",
    # Utilities
    "PromptBuilder",
]
