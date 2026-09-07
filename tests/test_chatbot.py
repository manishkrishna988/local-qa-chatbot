from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from streamlit.testing.v1 import AppTest

import chatbot
from chatbot import Settings, bounded_history, validate_question


def test_validation():
    assert validate_question("  hello  ") == "hello"
    for question in ["  ", "x" * 2001]:
        with pytest.raises(ValueError):
            validate_question(question)


def test_settings_reject_credentials(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://user:secret@example.com")
    with pytest.raises(ValueError):
        Settings.from_env()


def test_history_keeps_recent_complete_pairs():
    messages = [{"role": "user", "content": "x" * 4000},
                {"role": "assistant", "content": "y" * 4000},
                {"role": "user", "content": "recent question"},
                {"role": "assistant", "content": "recent answer"}]
    result = bounded_history(messages)
    assert [m.content for m in result] == ["recent question", "recent answer"]
    assert bounded_history([]) == []


def test_chain_streams(monkeypatch):
    monkeypatch.setattr(chatbot, "ChatOllama", lambda **kwargs:
                        FakeListChatModel(responses=["A test answer"]))
    chain = chatbot.build_chain(Settings())
    assert "".join(chain.stream({"question": "Hello", "history": []})) == "A test answer"


def test_ui_success_and_clear(monkeypatch):
    monkeypatch.setattr(chatbot, "ChatOllama", lambda **kwargs:
                        FakeListChatModel(responses=["A test answer"]))
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    assert not app.exception
    app.chat_input[0].set_value("Hello").run()
    assert not app.exception
    assert app.session_state["messages"][-1]["content"] == "A test answer"
    app.sidebar.button[0].click().run()
    assert app.session_state["messages"] == []


def test_failed_stream_does_not_save_partial_exchange(monkeypatch):
    class BrokenChain:
        def stream(self, payload):
            yield "partial answer"
            raise ConnectionError("sensitive details")
    monkeypatch.setattr(chatbot, "build_chain", lambda *args: BrokenChain())
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.chat_input[0].set_value("Hello").run()
    assert not app.exception
    assert app.session_state["messages"] == []
    assert "Could not complete" in app.error[0].value
    assert "sensitive details" not in app.error[0].value
