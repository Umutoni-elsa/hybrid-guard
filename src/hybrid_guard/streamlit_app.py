import sys
import time
from pathlib import Path
import streamlit as st
import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hybrid_guard.pipeline import run
from hybrid_guard.config import AUDIT_LOG_FILE, RISK_THRESHOLD, MODEL_NAME

st.set_page_config(page_title="Hybrid-Guard — prompt analysis", layout="wide")

# --- sidebar ---
with st.sidebar:
    st.title("Hybrid-Guard")
    page = st.radio("", ["Home", "Log", "Config"], label_visibility="collapsed")

# ================================================================
# HOME
# ================================================================
if page == "Home":
    st.title("Hybrid-Guard")
    st.caption("Prompt injection detector")

    prompt = st.text_area(
        "Enter prompt",
        placeholder="Paste or type a prompt to analyse...",
        height=130,
    )

    analyse = st.button("Analyse ↗", type="primary")

    if analyse:
        if not prompt.strip():
            st.warning("Please enter a prompt first.")
        else:
            with st.spinner("Analysing..."):
                start = time.time()
                try:
                    result = run(prompt, repeats=1)
                except Exception as e:
                    st.error(f"Pipeline error: {e}")
                    st.stop()
                elapsed = time.time() - start

            st.divider()
            st.subheader("Results")

            # risk score bar
            score = result["risk_score"]
            band = result["risk_band"]
            st.markdown(f"**Risk score**")
            st.progress(score / 100, text=f"{score} / 100")

            # verdict badge
            verdict = result["verdict"] or "SAFE"
            decision = result["decision"]

            badge_color = {
                "SAFE": "green",
                "SUSPICIOUS": "orange",
                "MALICIOUS": "red",
            }.get(verdict, "gray")

            st.markdown(
                f"""
                <div style="margin:8px 0">
                    <span style="background:{badge_color};color:white;
                    padding:6px 18px;border-radius:6px;font-weight:bold;
                    font-size:1rem">{verdict}</span>
                    &nbsp;&nbsp;
                    <span style="color:#888;font-size:0.9rem">
                    Decision: <b>{decision}</b></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # matched patterns
            if result["matched_patterns"]:
                st.markdown("**Matched patterns**")
                for p in result["matched_patterns"]:
                    st.markdown(f"- {p}")

            # rationale
            if result["rationale"]:
                st.markdown("**LLM rationale (Stage 2)**")
                st.info(result["rationale"])

            # normalisation actions
            if result["normalisation_actions"]:
                with st.expander("Normalisation actions applied"):
                    for a in result["normalisation_actions"]:
                        st.markdown(f"- {a}")

            st.caption(
                f"Analysed in {elapsed:.1f}s · "
                f"Escalated to Stage 2: {result['escalated']} · "
                f"Model: {MODEL_NAME}"
            )

# ================================================================
# LOG
# ================================================================
elif page == "Log":
    st.title("Audit log")

    if AUDIT_LOG_FILE.exists():
        df = pd.read_csv(AUDIT_LOG_FILE)
        st.dataframe(df[::-1], use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV", csv, "audit_log.csv", "text/csv"
        )
    else:
        st.info("No entries yet — analyse a prompt on the Home page first.")

# ================================================================
# CONFIG
# ================================================================
elif page == "Config":
    st.title("Configuration")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Risk threshold", f"{RISK_THRESHOLD} / 100")
        st.metric("Active model", MODEL_NAME)
    with col2:
        st.metric("Audit log", str(AUDIT_LOG_FILE))

    st.info(
        "To switch between the demo model (llama3.2:3b) and the "
        "production model (mistral:7b), edit MODEL_NAME in "
        "src/hybrid_guard/config.py and restart the app."
    )
