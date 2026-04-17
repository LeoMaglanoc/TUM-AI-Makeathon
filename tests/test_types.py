"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from src.core.types import ChatRequest, Message


class TestMessage:
    def test_valid_user_message(self):
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_valid_assistant_message(self):
        msg = Message(role="assistant", content="Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"

    def test_invalid_role_rejected(self):
        with pytest.raises(ValidationError):
            Message(role="system", content="not allowed")

    def test_empty_content_rejected(self):
        with pytest.raises(ValidationError):
            Message(role="user", content="")

    def test_whitespace_only_content_rejected(self):
        with pytest.raises(ValidationError):
            Message(role="user", content="   ")


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(messages=[Message(role="user", content="Hello")])
        assert len(req.messages) == 1

    def test_empty_messages_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(messages=[])

    def test_multi_turn_conversation(self):
        req = ChatRequest(
            messages=[
                Message(role="user", content="Hi"),
                Message(role="assistant", content="Hello!"),
                Message(role="user", content="How are you?"),
            ]
        )
        assert len(req.messages) == 3
