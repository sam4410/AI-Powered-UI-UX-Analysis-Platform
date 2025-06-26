# mockup_renderer.py

import re
import streamlit as st
from html import unescape

def extract_body_and_styles(html: str) -> str:
    """
    Extracts only the <style> and <body> content from a full HTML document.
    Streamlit's st.components.v1.html cannot render <html>, <head>, or full page markup.
    """
    if not isinstance(html, str):
        return ""

    # Unescape any HTML entities (in case LLM escaped it)
    html = unescape(html.strip())

    # Extract <style>
    style_match = re.search(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    style_block = f"<style>{style_match.group(1)}</style>" if style_match else ""

    # Extract <body>
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    body_content = body_match.group(1).strip() if body_match else html

    return f"{style_block}\n{body_content}"

def render_mockup_tab(mockup_html: str, download_filename: str = "mockup_wireframe.html"):
    """
    Render a mockup in Streamlit tab using cleaned HTML + provide download.
    """
    if not isinstance(mockup_html, str):
        st.warning("⚠️ Mockup content is not a string (after cleaning).")
        return
        
    mockup_html = mockup_html.strip()
    if not mockup_html:
        st.warning("⚠️ Mockup content is empty after stripping.")
        return

    # Clean HTML (remove full-page elements)
    cleaned_html = extract_body_and_styles(mockup_html)

    if "<" not in cleaned_html:
        st.warning("⚠️ Cleaned mockup doesn't contain valid HTML.")
        return

    try:
        st.components.v1.html(cleaned_html, height=700, scrolling=True)
        
        view_suffix = "_compare" if st.session_state.get("show_comparison") else "_normal"
        st.download_button(
            label="💾 Download Full HTML",
            data=mockup_html,
            file_name=download_filename,
            mime="text/html",
            key=f"html_mockup_download_btn{view_suffix}"
        )

        with st.expander("🔍 Show Raw HTML Output"):
            st.text_area("Raw Mockup Output", mockup_html, height=300)

    except Exception as e:
        st.error(f"❌ Failed to render mockup: {e}")
