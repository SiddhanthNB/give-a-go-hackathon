import os
import sys
import asyncio
import time
import streamlit as st
import lib.utils.constants as constants
from lib.agentic_ai.models import UserResponse
from lib.agentic_ai.pipeline import run_pipeline

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def render_ui():
    st.set_page_config(page_title="Hotel AI Strategist", page_icon="📈", layout="wide")

    st.title("Hotel AI Strategist")
    st.caption("Professional commercial insights driven by real-time data.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ex: 'Compare Executive room revenue this week vs last week'")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    start_ts = time.perf_counter()

                    response: UserResponse = asyncio.run(run_pipeline(user_input))

                    elapsed = time.perf_counter() - start_ts

                    st.subheader(response.headline)
                    st.markdown(response.analysis)

                    if response.recommendations:
                        st.info("**Recommendations:**\n\n" + "\n".join([f"- {r}" for r in response.recommendations]))

                    if response.status == "success":
                        st.caption(f"Analysis completed in {elapsed:.2f}s")

                    full_reply = f"### {response.headline}\n\n{response.analysis}"
                    st.session_state.messages.append({"role": "assistant", "content": full_reply})

                except Exception as exc:
                    st.error(f"Pipeline Error: {exc}")

if __name__ == "__main__":
    render_ui()