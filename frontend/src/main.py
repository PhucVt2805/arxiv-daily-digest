import streamlit as st
import httpx
import os

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Arxiv Research Agent", layout="wide")

st.markdown("""
<style>
    .reportview-container { margin-top: -2em; }
    .stDeployButton {display:none;}
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if "selected_paper" not in st.session_state:
    st.session_state.selected_paper = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def fetch_daily_news():
    """Call the Backend API to retrieve the list of articles."""
    try:
        resp = httpx.get(f"{BACKEND_URL}/news/latest") 
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        st.error(f"Backend not connected: {e}")
        return []

def reset_chat():
    st.session_state.messages = []
    st.session_state.selected_paper = None

# ==========================================
# SCREEN 1: NEWS LIST (DASHBOARD)
# ==========================================
if not st.session_state.selected_paper:
    st.title("📰 Arxiv Computer Science Daily")
    st.caption("Stay up-to-date with the latest research on AI, CV, and NLP from arXiv.")

    with st.spinner("Loading today's news..."):
        papers = fetch_daily_news()

    if not papers:
        st.info("No articles have been updated today.")
    else:
        for paper in papers:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(paper['title'])
                    st.text(f"Authors: {', '.join(paper.get('authors', []))[:50]}...")
                    st.markdown(f"**Published:** {paper['published_date'][:10]} | **Cat:** {paper['prime_category']}")
                    with st.expander("Xem tóm tắt"):
                        st.write(paper['summary'])
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("💬 Chat & Research", key=paper['_id']):
                        st.session_state.selected_paper = paper
                        st.session_state.messages = [{
                            "role": "assistant",
                            "content": f"Chào bạn! Tôi đã đọc qua bài báo **'{paper['title']}'**. Bạn muốn tìm hiểu sâu về khía cạnh nào (Methodology, Experiments, hay Conclusion)?"
                        }]
                        st.rerun()

# ==========================================
# SCREEN 2: CHATBOT (DEEP DIVE)
# ==========================================
else:
    paper = st.session_state.selected_paper
    with st.sidebar:
        if st.button("⬅️ Quay lại danh sách"):
            reset_chat()
            st.rerun()
        
        st.header("Research Context")
        st.info(f"**{paper['title']}**")
        st.markdown(f"[Link PDF]({paper['pdf_url']})")
        st.markdown("### Abstract")
        st.caption(paper['summary'])

    st.title("🤖 Research Assistant")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi gì đó về bài báo này..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                with httpx.stream(
                    "POST", 
                    f"{BACKEND_URL}/chat/stream", 
                    json={
                        "paper_id": paper['_id'],
                        "message": prompt,
                        "history": st.session_state.messages[:-1]
                    },
                    timeout=60.0
                ) as response:
                    for chunk in response.iter_text():
                        if chunk:
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                            
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"AI connection error: {e}")