from datetime import date
from html import escape as html_escape

import streamlit as st
from bs4 import BeautifulSoup
from markdown import markdown


def parse_text(markdown_text: str) -> str:
    html = markdown(markdown_text)
    plain_text = BeautifulSoup(html, "html.parser").get_text()
    return plain_text.replace("$", r"\$")


def get_dynamic_suggestions(ref_date: date) -> dict[str, str]:
    month_name = ref_date.strftime("%B")
    return {
        "Monthly Risks": f"Identify commercial risks or high cancellations for {month_name}",
        "Revenue Pacing": "Compare revenue performance this month vs last month",
        "ADR Leaders": "Which room type is generating the highest ADR right now?",
        "Distribution Mix": "Analyze dependency on OTA channels for upcoming bookings",
    }


def apply_clean_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #3f3f46;
        }

        /* Sidebar: Clean light grey */
        [data-testid="stSidebar"] {
            background-color: #f8f9fb;
            border-right: 1px solid #e6e9ef;
        }

        .sidebar-header {
            font-size: 11px;
            font-weight: 700;
            color: #a1a1aa;
            text-transform: uppercase;
            letter-spacing: 0.1rem;
            margin-bottom: 20px;
        }

        /* Message Styling */
        [data-testid="stChatMessage"]:nth-child(even) {
            background-color: #f4f4f5 !important;
            border-radius: 8px;
            padding: 20px;
        }

        /* Buttons */
        div.stButton > button {
            border-radius: 4px;
            font-size: 14px;
        }

        /* Recommendation card */
        .rec-card {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 14px 16px;
        }
        .rec-title {
            font-weight: 600;
            margin-bottom: 8px;
            color: #111827;
        }
        .rec-list {
            margin: 0;
            padding-left: 18px;
        }
        .rec-list li {
            margin: 6px 0;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_recommendations(recommendations: list[str]) -> None:
    if not recommendations:
        return
    items = "\n".join(f"<li>{html_escape(parse_text(rec))}</li>" for rec in recommendations)
    st.markdown(
        f"""
        <div class="rec-card">
            <div class="rec-title">Recommended Actions</div>
            <ul class="rec-list">
                {items}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_highlights(highlights: list[str]) -> None:
    if not highlights:
        return
    st.markdown("**Highlights**")
    items = "\n".join(f"- {html_escape(parse_text(h))}" for h in highlights)
    st.markdown(items)
