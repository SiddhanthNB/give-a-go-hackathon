import os
import sys
import time
import streamlit as st
from datetime import date, datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import lib.utils.constants as constants
from lib.agentic_ai.models import UserResponse
from lib.agentic_ai.pipeline import run_pipeline
from lib.utils.streamlit_helper import (
    apply_clean_theme,
    get_dynamic_suggestions,
    parse_text,
    render_highlights,
    render_recommendations,
)

TEMPORARY_AGENT_RESPONSE = {
    "success": True,
    "error": None,
    "data": {
        "headline": "June Corporate Pickup Collapse—Immediate Intervention Required",
        "highlights": [
            "Corporate room nights are down **42% vs STLY** for June, while transient is up 9%.",
            "ADR slipped from **$212 to $187** MoM, despite occupancy holding flat at 78%.",
            "Cancellations in Corporate spiked to **19%**, double the 9% trailing average.",
            "Group demand is pacing **$64K behind** last month at this time.",
        ],
        "judgment": "The pace shortfall is concentrated in Corporate and Group, suggesting a pipeline or account disruption rather than a market-wide demand dip. Holding occupancy flat while ADR falls indicates discounted fill, which is masking underlying segment weakness. Without a near-term recovery plan, July will likely open with a low-rate mix that erodes RevPAR.",
        "recommendations": [
            "Launch a 72-hour account recovery sprint for top 20 Corporate accounts with open blocks or stalled RFPs.",
            "Reprice midweek Corporate BAR by +$10 and shift discounts to fenced offers to protect ADR.",
            "Build a 10-day Group blitz list with minimum value thresholds and approval fast-track."
        ],
    },
}

def render_ui():
    st.set_page_config(page_title="The Night Manager", page_icon="🌙", layout="wide")
    apply_clean_theme()

    current_ts = datetime.combine(date(2026, 5, 15), datetime.min.time())
    suggestions = get_dynamic_suggestions(current_ts.date())

    with st.sidebar:
        st.markdown('<div class="sidebar-header">Pinned Queries</div>', unsafe_allow_html=True)
        pinned = st.session_state.get("pinned_queries", [])
        if not pinned:
            st.caption("No queries pinned yet.")
        else:
            for q in pinned:
                if st.button(f"{q[:30]}...", key=f"p_{q}", use_container_width=True):
                    st.session_state.active_query = q

        st.divider()
        st.caption(f"Simulation: {current_ts.date().strftime('%B %Y')}")

    # --- HEADER ---
    title_container = st.container()
    has_response = "current_response" in st.session_state

    with title_container:
        col_title, col_restart = st.columns([0.8, 0.2], vertical_alignment="bottom")
        with col_title:
            st.title("The Night Manager", anchor=False)
            st.write("Your AI-Powered Hotel Performance Analyst. Ask questions about your hotel's commercial performance and get strategic insights in seconds.")
        with col_restart:
            if has_response:
                if st.button("Restart", type="secondary", use_container_width=True):
                    st.session_state.pop("current_query", None)
                    st.session_state.pop("current_response", None)
                    st.rerun()

    # --- INPUT LOGIC ---
    user_msg = st.chat_input("Ask me a commercial question...")

    # Handle Pinned/Pills
    if not user_msg:
        if not has_response:
            selected_pill = st.pills("Strategic Focus", list(suggestions.keys()), label_visibility="collapsed")
            if selected_pill:
                user_msg = suggestions[selected_pill]
        if "active_query" in st.session_state:
            user_msg = st.session_state.active_query
            del st.session_state.active_query

    if has_response:
        with st.chat_message("user"):
            st.write(parse_text(st.session_state.current_query))

        with st.chat_message("assistant"):
            full_resp = st.session_state.current_response

            if full_resp.success and full_resp.data:
                outcome = full_resp.data

                st.write(f"**{parse_text(outcome.headline)}**")

                if outcome.highlights:
                    render_highlights(outcome.highlights)
                    st.write(" ")

                st.write(parse_text(outcome.judgment))

                if outcome.recommendations:
                    st.write(" ")
                    render_recommendations(outcome.recommendations)

                st.write(" ")

                if st.button("Pin Query"):
                    if "pinned_queries" not in st.session_state:
                        st.session_state.pinned_queries = []
                    if st.session_state.current_query not in st.session_state.pinned_queries:
                        st.session_state.pinned_queries.append(st.session_state.current_query)
                        st.toast("Query pinned.")
            else:
                st.error(f"Error: {full_resp.error or 'Unknown error'}")

    if user_msg:
        st.session_state.current_query = user_msg

        with st.status("Analyzing Commercial Data...", expanded=False) as status:
            time.sleep(0.8) # Simulated SQL Engine
            status.update(label="Analysis complete", state="complete")

        #resp = asyncio.run(run_pipeline(user_msg, current_ts))
        resp = UserResponse.model_validate(TEMPORARY_AGENT_RESPONSE)
        st.session_state.current_response = resp
        st.rerun()
