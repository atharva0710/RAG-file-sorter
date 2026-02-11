"""
main_dashboard.py — Streamlit dashboard for Content Alchemist.

Two tabs:
  • Recent  — table of the last 20 processed files.
  • Query   — chat-style search over the summary column.

Usage:
    streamlit run main_dashboard.py
"""

import streamlit as st
import pandas as pd
from db import Logger

# ── Page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Content Alchemist",
    page_icon="🧪",
    layout="wide",
)

logger = Logger()

# ── Header ──────────────────────────────────────────────────────────
st.title("🧪 Content Alchemist")
st.caption("RAG-based Intelligent Auto-tagger — file dashboard")

# ── Tabs ────────────────────────────────────────────────────────────
tab_recent, tab_query = st.tabs(["📋 Recent", "🔍 Query"])

# ── Column rename map ──────────────────────────────────────────────
DISPLAY_COLS = {
    "original_filename": "Original Filename",
    "new_filename":      "New Filename",
    "category":          "Category",
    "summary":           "Summary",
    "timestamp":         "Processed At",
}


def _show_table(records: list[dict]):
    """Render a list of records as a pretty Streamlit dataframe."""
    if not records:
        st.info("No files found.")
        return

    df = pd.DataFrame(records)
    cols = [c for c in DISPLAY_COLS if c in df.columns]
    df_display = df[cols].rename(columns=DISPLAY_COLS)

    st.dataframe(df_display, use_container_width=True, hide_index=True)


# ── Tab 1: Recent ──────────────────────────────────────────────────
with tab_recent:
    st.subheader("Last 20 processed files")
    recent = logger.get_recent(limit=20)
    _show_table(recent)
    st.caption(f"Total files in database: {len(logger.get_all())}")


# ── Tab 2: Query ───────────────────────────────────────────────────
with tab_query:
    st.subheader("Search your library")
    st.caption('Ask something like **"What papers are about Biology?"** — '
               "we'll keyword-search the summary column.")

    user_query = st.chat_input("Ask about your files…")

    if user_query:
        # Echo the question
        with st.chat_message("user"):
            st.write(user_query)

        # Search and respond
        results = logger.search_summary(user_query)

        with st.chat_message("assistant"):
            if results:
                st.write(f"Found **{len(results)}** matching file(s):")
                _show_table(results)
            else:
                st.write("No files matched your query. Try different keywords.")


# ── Footer ──────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Run the watcher in a separate terminal: `python watcher.py` · "
    "This dashboard reads from the shared SQLite database."
)
