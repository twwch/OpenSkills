"""Tests for the LLM module."""

import base64
import pytest
from pathlib import Path

from openskills.llm import (
    Message,
    ImageContent,
    TextContent,
    ImageDetail,
    image_url,
    image_file,
    image_base64,
    text,
)


class TestTextContent:
    """Tests for TextContent."""

    def test_text_content_creation(self):
        content = TextContent(text="Hello, world!")
        assert content.text == "Hello, world!"
        assert content.type == "text"

    def test_text_content_to_dict(self):
        content = TextContent(text="Hello")
        result = content.to_dict()
        assert result == {"type": "text", "text": "Hello"}

    def test_text_helper(self):
        content = text("Hello")
        assert isinstance(content, TextContent)
        assert content.text == "Hello"


class TestImageContent:
    """Tests for ImageContent."""

    def test_image_from_url(self):
        img = ImageContent(url="https://example.com/image.jpg")
        assert img.url == "https://example.com/image.jpg"
        assert img.get_url() == "https://example.com/image.jpg"

    def test_image_from_base64(self):
        data = base64.b64encode(b"fake image data").decode()
        img = ImageContent(base64_data=data, media_type="image/png")
        assert img.base64_data == data
        assert "data:image/png;base64," in img.get_url()

    def test_image_url_helper(self):
        img = image_url("https://example.com/img.jpg", detail=ImageDetail.HIGH)
        assert img.url == "https://example.com/img.jpg"
        assert img.detail == ImageDetail.HIGH

    def test_image_base64_helper(self):
        data = "fakeb64data"
        img = image_base64(data, media_type="image/png", detail=ImageDetail.LOW)
        assert img.base64_data == data
        assert img.media_type == "image/png"
        assert img.detail == ImageDetail.LOW

    def test_image_to_dict(self):
        img = ImageContent(url="https://example.com/img.jpg", detail=ImageDetail.AUTO)
        result = img.to_dict()

        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == "https://example.com/img.jpg"
        assert result["image_url"]["detail"] == "auto"

    def test_image_no_data_raises(self):
        img = ImageContent()  # No url, base64, or file_path
        with pytest.raises(ValueError):
            img.get_url()


class TestMessage:
    """Tests for Message."""

    def test_simple_text_message(self):
        msg = Message(role="user", content="Hello!")
        assert msg.role == "user"
        assert msg.content == "Hello!"
        assert not msg.is_multimodal()

    def test_message_class_methods(self):
        user_msg = Message.user("Hello")
        assert user_msg.role == "user"
        assert user_msg.content == "Hello"

        assistant_msg = Message.assistant("Hi there")
        assert assistant_msg.role == "assistant"

        system_msg = Message.system("You are helpful")
        assert system_msg.role == "system"

    def test_multimodal_message(self):
        img = ImageContent(url="https://example.com/img.jpg")
        msg = Message(
            role="user",
            content="What's in this image?",
            images=[img]
        )

        assert msg.is_multimodal()
        assert len(msg.images) == 1

    def test_multimodal_message_classmethod(self):
        img = ImageContent(url="https://example.com/img.jpg")
        msg = Message.user("Describe this", images=[img])

        assert msg.is_multimodal()
        assert msg.role == "user"

    def test_text_message_to_api_content(self):
        msg = Message(role="user", content="Hello")
        content = msg.to_api_content()

        # Text-only returns string
        assert content == "Hello"

    def test_multimodal_message_to_api_content(self):
        img = ImageContent(url="https://example.com/img.jpg")
        msg = Message(
            role="user",
            content="What's this?",
            images=[img]
        )
        content = msg.to_api_content()

        # Multimodal returns list
        assert isinstance(content, list)
        assert len(content) == 2

        # First is text
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "What's this?"

        # Second is image
        assert content[1]["type"] == "image_url"
        assert content[1]["image_url"]["url"] == "https://example.com/img.jpg"

    def test_message_to_dict(self):
        msg = Message(role="user", content="Hello")
        result = msg.to_dict()

        assert result["role"] == "user"
        assert result["content"] == "Hello"

    def test_multimodal_message_to_dict(self):
        img = ImageContent(url="https://example.com/img.jpg")
        msg = Message(
            role="user",
            content="Describe",
            images=[img]
        )
        result = msg.to_dict()

        assert result["role"] == "user"
        assert isinstance(result["content"], list)

    def test_message_with_name(self):
        msg = Message(role="user", content="Hello", name="Alice")
        result = msg.to_dict()

        assert result["name"] == "Alice"

    def test_multiple_images(self):
        images = [
            ImageContent(url="https://example.com/1.jpg"),
            ImageContent(url="https://example.com/2.jpg"),
        ]
        msg = Message(
            role="user",
            content="Compare these images",
            images=images,
        )

        content = msg.to_api_content()

        # 1 text + 2 images
        assert len(content) == 3
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image_url"
        assert content[2]["type"] == "image_url"


class TestImageFromFile:
    """Tests for loading images from files."""

    def test_image_from_file(self, tmp_path):
        # Create a test image file
        img_path = tmp_path / "test.png"
        img_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # Minimal PNG-like data
        img_path.write_bytes(img_data)

        # Load from file
        img = ImageContent(file_path=img_path)

        assert img.base64_data is not None
        assert img.media_type == "image/png"

        # Can get URL
        url = img.get_url()
        assert url.startswith("data:image/png;base64,")

    def test_image_file_helper(self, tmp_path):
        img_path = tmp_path / "test.jpg"
        img_path.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)  # JPEG magic

        img = image_file(str(img_path))

        assert img.base64_data is not None
        assert "jpeg" in img.media_type

    def test_image_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            ImageContent(file_path=Path("/nonexistent/image.jpg"))


class TestImageDetail:
    """Tests for ImageDetail enum."""

    def test_image_detail_values(self):
        assert ImageDetail.LOW.value == "low"
        assert ImageDetail.HIGH.value == "high"
        assert ImageDetail.AUTO.value == "auto"

    def test_image_detail_in_dict(self):
        img = ImageContent(url="https://example.com/img.jpg", detail=ImageDetail.HIGH)
        result = img.to_dict()

        assert result["image_url"]["detail"] == "high"
