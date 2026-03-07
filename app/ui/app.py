import os
import sys
import asyncio
import httpx
import streamlit as st

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import lib.utils.constants as constants


st.set_page_config(page_title="Hotel Assistant", page_icon="H", layout="centered")

st.title("Hotel Assistant")
st.caption("Ask a question. The UI calls the local FastAPI backend.")

print("[DEBUG][ui] app loaded")

def render_ui():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about hotel performance, pickup, or risk...")

    if user_input:
        print("[DEBUG][ui] user input received")
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    print("[DEBUG][ui] importing agent")
                    from lib.agentic_ai.agents.insight_agent import insight_agent
                    from lib.helpers.formatting import format_reply

                    print("[DEBUG][ui] running agent")
                    result = asyncio.run(insight_agent.run(user_input))
                    print("[DEBUG][ui] agent run complete")
                    reply = format_reply(result.output)
                except Exception as exc:
                    print(f"[DEBUG][ui] agent error: {exc}")
                    reply = f"Agent error: {exc}"
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        print("[DEBUG][ui] reply rendered")
