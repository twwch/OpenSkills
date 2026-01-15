"""
Base LLM client interface.

Defines the abstract interface for LLM clients with support for
multimodal messages (text + images).
"""

import base64
import mimetypes
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import AsyncIterator, Union


class ContentType(str, Enum):
    """Type of content in a message."""
    TEXT = "text"
    IMAGE_URL = "image_url"
    IMAGE_BASE64 = "image_base64"


class ImageDetail(str, Enum):
    """Image detail level for vision models."""
    LOW = "low"
    HIGH = "high"
    AUTO = "auto"


@dataclass
class TextContent:
    """Text content part of a message."""
    type: str = field(default="text", init=False)
    text: str = ""

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {"type": "text", "text": self.text}


@dataclass
class ImageContent:
    """
    Image content part of a message.

    Supports three input methods:
    1. URL: Direct image URL
    2. Base64: Base64-encoded image data
    3. File path: Local file path (automatically converted to base64)
    """
    type: str = field(default="image_url", init=False)
    url: str | None = None
    base64_data: str | None = None
    file_path: Path | None = None
    media_type: str = "image/jpeg"
    detail: ImageDetail = ImageDetail.AUTO

    def __post_init__(self):
        """Load image from file if file_path is provided."""
        if self.file_path and not self.base64_data and not self.url:
            self._load_from_file()

    def _load_from_file(self):
        """Load image data from file."""
        if not self.file_path:
            return

        path = Path(self.file_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")

        # Detect media type
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type:
            self.media_type = mime_type

        # Read and encode
        with open(path, "rb") as f:
            self.base64_data = base64.b64encode(f.read()).decode("utf-8")

    def get_url(self) -> str:
        """Get the image URL (converts base64 to data URL if needed)."""
        if self.url:
            return self.url
        if self.base64_data:
            return f"data:{self.media_type};base64,{self.base64_data}"
        raise ValueError("No image data available")

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "type": "image_url",
            "image_url": {
                "url": self.get_url(),
                "detail": self.detail.value,
            }
        }


# Content can be text or image
MessageContent = Union[TextContent, ImageContent]


@dataclass
class Message:
    """
    A chat message with support for multimodal content.

    Examples:
        # Simple text message
        msg = Message(role="user", content="Hello!")

        # Message with image URL
        msg = Message(
            role="user",
            content="What's in this image?",
            images=[ImageContent(url="https://example.com/image.jpg")]
        )

        # Message with local image file
        msg = Message(
            role="user",
            content="Describe this image",
            images=[ImageContent(file_path=Path("./photo.jpg"))]
        )

        # Message with base64 image
        msg = Message(
            role="user",
            content="Analyze this",
            images=[ImageContent(base64_data="...", media_type="image/png")]
        )
    """
    role: str  # "system", "user", "assistant"
    content: str = ""
    images: list[ImageContent] = field(default_factory=list)
    name: str | None = None  # Optional name for the message author

    def is_multimodal(self) -> bool:
        """Check if this message contains images."""
        return len(self.images) > 0

    def to_api_content(self) -> str | list[dict]:
        """
        Convert content to API format.

        Returns string for text-only, list for multimodal.
        """
        if not self.is_multimodal():
            return self.content

        parts = []

        # Add text content first
        if self.content:
            parts.append(TextContent(text=self.content).to_dict())

        # Add images
        for image in self.images:
            parts.append(image.to_dict())

        return parts

    def to_dict(self) -> dict:
        """Convert to API message format."""
        result = {
            "role": self.role,
            "content": self.to_api_content(),
        }
        if self.name:
            result["name"] = self.name
        return result

    @classmethod
    def user(cls, content: str, images: list[ImageContent] | None = None) -> "Message":
        """Create a user message."""
        return cls(role="user", content=content, images=images or [])

    @classmethod
    def assistant(cls, content: str) -> "Message":
        """Create an assistant message."""
        return cls(role="assistant", content=content)

    @classmethod
    def system(cls, content: str) -> "Message":
        """Create a system message."""
        return cls(role="system", content=content)


@dataclass
class ToolCall:
    """A tool/function call from the model."""
    id: str
    name: str
    arguments: str  # JSON string


@dataclass
class ChatResponse:
    """Response from a chat completion."""
    content: str
    model: str = ""
    usage: dict = field(default_factory=dict)
    finish_reason: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def prompt_tokens(self) -> int:
        """Get prompt token count."""
        return self.usage.get("prompt_tokens", 0)

    @property
    def completion_tokens(self) -> int:
        """Get completion token count."""
        return self.usage.get("completion_tokens", 0)

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        return self.usage.get("total_tokens", 0)


@dataclass
class StreamChunk:
    """A chunk from a streaming response."""
    content: str = ""
    finish_reason: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients.

    Implementations should provide:
    - chat(): Single response completion
    - chat_stream(): Streaming response completion

    Features:
    - Multimodal support (text + images)
    - Streaming responses
    - Tool/function calling (optional)
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> ChatResponse:
        """
        Send a chat completion request.

        Args:
            messages: List of chat messages (can include images)
            system: Optional system prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific options

        Returns:
            ChatResponse with the completion
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[Message],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """
        Send a streaming chat completion request.

        Args:
            messages: List of chat messages (can include images)
            system: Optional system prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific options

        Yields:
            StreamChunk objects as they arrive
        """
        pass

    def create_message(
        self,
        role: str,
        content: str,
        images: list[ImageContent] | None = None,
    ) -> Message:
        """Create a message object."""
        return Message(role=role, content=content, images=images or [])

    def create_image_from_url(
        self,
        url: str,
        detail: ImageDetail = ImageDetail.AUTO,
    ) -> ImageContent:
        """Create an image content from URL."""
        return ImageContent(url=url, detail=detail)

    def create_image_from_file(
        self,
        file_path: str | Path,
        detail: ImageDetail = ImageDetail.AUTO,
    ) -> ImageContent:
        """Create an image content from file."""
        return ImageContent(file_path=Path(file_path), detail=detail)

    def create_image_from_base64(
        self,
        base64_data: str,
        media_type: str = "image/jpeg",
        detail: ImageDetail = ImageDetail.AUTO,
    ) -> ImageContent:
        """Create an image content from base64 data."""
        return ImageContent(
            base64_data=base64_data,
            media_type=media_type,
            detail=detail,
        )


# Convenience aliases
def text(content: str) -> TextContent:
    """Create a text content part."""
    return TextContent(text=content)


def image_url(url: str, detail: ImageDetail = ImageDetail.AUTO) -> ImageContent:
    """Create an image content from URL."""
    return ImageContent(url=url, detail=detail)


def image_file(path: str | Path, detail: ImageDetail = ImageDetail.AUTO) -> ImageContent:
    """Create an image content from file path."""
    return ImageContent(file_path=Path(path), detail=detail)


def image_base64(
    data: str,
    media_type: str = "image/jpeg",
    detail: ImageDetail = ImageDetail.AUTO,
) -> ImageContent:
    """Create an image content from base64 data."""
    return ImageContent(base64_data=data, media_type=media_type, detail=detail)
