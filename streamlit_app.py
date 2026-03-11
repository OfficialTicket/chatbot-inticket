import streamlit as st
from openai import OpenAI

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Messages", page_icon="💬", layout="centered")

# ── iMessage CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Font: SF Pro 대체용 ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
        background-color: #f2f2f7 !important;
        color: #1c1c1e;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header, .stDeployButton { display: none !important; }
    .block-container {
        padding: 0 !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }

    /* ── Status bar (top) ── */
    .status-bar {
        position: sticky;
        top: 0;
        z-index: 100;
        background: rgba(242,242,247,0.9);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 0.5px solid rgba(0,0,0,0.1);
        padding: 12px 16px 10px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .contact-name  { font-size: 15px; font-weight: 600; color: #1c1c1e; line-height: 1.2; }
    .contact-sub   { font-size: 11px; color: #8e8e93; margin-top: 1px; }
    .avatar-circle {
        width: 36px; height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #5E5CE6 0%, #BF5AF2 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 16px; flex-shrink: 0;
    }
    .contact-info { flex: 1; }

    /* ── Message list area ── */
    .chat-area {
        padding: 12px 12px 8px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    /* ── Individual bubble wrapper ── */
    .msg-row {
        display: flex;
        align-items: flex-end;
        gap: 6px;
        animation: fadeSlideUp 0.25s ease-out both;
        margin-bottom: 8px;
    }
    .msg-row.user  { flex-direction: row-reverse; }
    .msg-row.assistant { flex-direction: row; }

    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Bubble ── */
    .bubble {
        max-width: 72%;
        padding: 9px 14px;
        border-radius: 18px;
        font-size: 15px;
        line-height: 1.45;
        word-break: break-word;
        position: relative;
    }

    /* user → blue iMessage bubble */
    .msg-row.user .bubble {
        background: #0A84FF;
        color: #ffffff;
        border-bottom-right-radius: 4px;
    }

    /* assistant → light grey bubble */
    .msg-row.assistant .bubble {
        background: #e9e9eb;
        color: #1c1c1e;
        border-bottom-left-radius: 4px;
        border: none;
    }

    /* ── Mini avatar for assistant ── */
    .mini-avatar {
        width: 24px; height: 24px;
        border-radius: 50%;
        background: linear-gradient(135deg, #5E5CE6 0%, #BF5AF2 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 11px; flex-shrink: 0; margin-bottom: 2px;
    }

    /* ── Timestamp ── */
    .timestamp-row {
        text-align: center;
        font-size: 11px;
        color: #aeaeb2;
        margin: 8px 0 4px;
        font-weight: 500;
    }

    /* ── Typing indicator ── */
    .typing-indicator {
        display: flex; align-items: center; gap: 6px;
        padding: 8px 12px;
    }
    .typing-dots {
        background: #1c1c1e;
        border-radius: 14px;
        padding: 8px 14px;
        display: flex; gap: 4px; align-items: center;
    }
    .dot {
        width: 7px; height: 7px;
        background: #636366; border-radius: 50%;
        animation: bounce 1.2s infinite;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 60%, 100% { transform: translateY(0); }
        30%            { transform: translateY(-5px); }
    }

    /* ── Input bar ── */
    .stChatInputContainer, [data-testid="stChatInput"] {
        background: #f2f2f7 !important;
        border-top: 0.5px solid rgba(0,0,0,0.1) !important;
        padding: 8px 12px 12px !important;
    }
    [data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        color: #1c1c1e !important;
        border-radius: 20px !important;
        border: 0.5px solid rgba(0,0,0,0.15) !important;
        padding: 9px 16px !important;
        font-size: 15px !important;
        font-family: 'Inter', sans-serif !important;
        resize: none !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: #aeaeb2 !important; }
    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(10,132,255,0.6) !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(10,132,255,0.15) !important;
    }

    /* Send button → blue circle */
    [data-testid="stChatInputSubmitButton"] {
        background: #0A84FF !important;
        border-radius: 50% !important;
        width: 32px !important; height: 32px !important;
        min-width: 32px !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(10,132,255,0.4) !important;
    }
    [data-testid="stChatInputSubmitButton"] svg {
        fill: #ffffff !important;
        width: 16px !important; height: 16px !important;
    }

    /* ── API key input ── */
    [data-testid="stTextInput"] input {
        background: #ffffff !important;
        color: #1c1c1e !important;
        border: 0.5px solid rgba(0,0,0,0.15) !important;
        border-radius: 12px !important;
        font-size: 15px !important;
    }
    [data-testid="stTextInput"] label {
        color: #636366 !important;
        font-size: 13px !important;
    }

    /* ── Info / warning boxes ── */
    [data-testid="stAlert"] {
        background: #ffffff !important;
        border: 0.5px solid rgba(0,0,0,0.08) !important;
        border-radius: 12px !important;
        color: #1c1c1e !important;
        font-size: 14px !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #c7c7cc; border-radius: 2px; }

    /* ── Typing dots 라이트모드 ── */
    .typing-dots { background: #e9e9eb; }
    .dot { background: #aeaeb2; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header (iMessage-style contact bar) ──────────────────────────────────────
st.markdown(
    """
    <div class="status-bar">
        <div class="avatar-circle">🐶</div>
        <div class="contact-info">
            <div class="contact-name">InTicket</div>
            <div class="contact-sub">iMessage · Active Now</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── API key ───────────────────────────────────────────────────────────────────
openai_api_key = st.text_input("OpenAI API Key", type="password", label_visibility="collapsed",
                                placeholder="🔑  OpenAI API Key를 입력하세요")
if not openai_api_key:
    st.info("OpenAI API Key를 입력하면 대화를 시작할 수 있어요.", icon="🔑")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render existing messages ──────────────────────────────────────────────────
def render_bubble(role: str, content: str):
    if role == "user":
        st.markdown(
            f"""
            <div class="msg-row user">
                <div class="bubble">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="msg-row assistant">
                <div class="mini-avatar">🐶</div>
                <div class="bubble">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Date separator
if st.session_state.messages:
    st.markdown('<div class="timestamp-row">오늘</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    render_bubble(msg["role"], msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("문자 메시지"):
    # User bubble
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_bubble("user", prompt)

    # Typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown(
        """
        <div class="typing-indicator">
            <div class="mini-avatar">🐶</div>
            <div class="typing-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stream response
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )
    response_text = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        response_text += delta

    # Remove typing indicator, show bubble
    typing_placeholder.empty()
    render_bubble("assistant", response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})