"""Run with: streamlit run app.py."""
import logging
import time

import streamlit as st

from chatbot import (
    MAX_INPUT_CHARS,
    MAX_STORED_MESSAGES,
    Settings,
    bounded_history,
    build_chain,
    validate_question,
)

logger = logging.getLogger(__name__)
st.set_page_config(page_title="Local Q&A", page_icon="💬", layout="centered")
st.title("Local Q&A")
st.caption("A small chatbot powered by LangChain, Streamlit and Ollama")
try:
    settings = Settings.from_env()
except ValueError as error:
    st.error(str(error))
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Your assistant")
    st.code(settings.model, language=None)
    temperature = st.slider("Creativity", 0.0, 1.0, 0.2, 0.1,
                            help="Lower values generally produce more consistent answers.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Recent exchanges provide context. History is temporary and may reset "
               "on reload or restart. Clearing removes it from this session.")
    st.caption("Answers can be wrong. This assistant does not search the internet.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question…", max_chars=MAX_INPUT_CHARS)
if question:
    try:
        question = validate_question(question)
    except ValueError as error:
        st.warning(str(error))
        st.stop()
    with st.chat_message("user"):
        st.markdown(question)
    started = time.monotonic()
    with st.chat_message("assistant"):
        output = st.empty()
        answer = ""
        try:
            chain = build_chain(settings, temperature)
            for chunk in chain.stream({"question": question,
                                       "history": bounded_history(st.session_state.messages)}):
                answer += chunk
                output.markdown(answer + " ▌")
            if not answer.strip():
                raise RuntimeError("Empty model response")
            output.markdown(answer)
        except Exception as error:  # noqa: BLE001 - contain provider failures at UI boundary
            # Do not log prompts, answers, endpoint credentials or raw exception text.
            logger.warning("generation_failed error_type=%s", type(error).__name__)
            output.empty()
            st.error("Could not complete the answer. Check that Ollama is running and "
                     "the configured model has been pulled, then try again. "
                     "This exchange was not saved.")
        else:
            st.session_state.messages.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ])
            st.session_state.messages = st.session_state.messages[-MAX_STORED_MESSAGES:]
            st.caption(f"Answered in {time.monotonic() - started:.1f}s")
