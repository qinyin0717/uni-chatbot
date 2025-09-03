import os
import streamlit as st
from dotenv import load_dotenv

# Optional: Gemini SDK (app still runs without it)
try:
    import google.generativeai as genai
except Exception:
    genai = None

# Load .env locally (use Secrets on cloud)
load_dotenv()

# -----------------------------
# Streamlit page setup
# -----------------------------
st.set_page_config(page_title="Uni Life Chatbot", page_icon="🎓", layout="centered")
st.title("🎓 Uni Life Chatbot")
st.caption("UI + Rule/AI + ≥5 custom answers + history + deployable (Streamlit).")

# Conversation memory
if "history" not in st.session_state:
    st.session_state.history = []  # list[dict]: {"role": "user"/"assistant", "content": "..."}

# -----------------------------
# Load FAQs (custom knowledge)
# Format per line: "question||answer"
# Match rule: longest keyword first
# -----------------------------
FAQ_PATH = "faqs.txt"
faq_pairs = []
if os.path.exists(FAQ_PATH):
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "||" not in line:
                continue
            q, a = line.split("||", 1)
            faq_pairs.append((q.lower().strip(), a.strip()))

def faq_lookup(user_text: str):
    """Return FAQ answer by longest-keyword match; None if no hit."""
    text = (user_text or "").lower()
    best = None
    best_len = 0
    for q, a in faq_pairs:
        if q and q in text and len(q) > best_len:
            best = a
            best_len = len(q)
    return best

# -----------------------------
# Sidebar options (Gemini optional)
# -----------------------------
with st.sidebar:
    st.header("⚙️ Options")
    use_gemini = st.toggle("Use Gemini if no FAQ match", value=False)
    # Prefer environment var (.env or cloud Secrets); allow manual override
    default_key = os.getenv("GOOGLE_API_KEY", "")
    google_api_key = st.text_input("GOOGLE_API_KEY", type="password", value=default_key)
    system_prompt = st.text_area(
        "System Prompt (for Gemini)",
        value=(
            "You are a concise, helpful university life assistant. "
            "Use short paragraphs or bullet points. If info may vary by campus, say it. "
            "End with a one-line TL;DR."
        ),
        height=120
    )

def gemini_answer(messages: list[dict], api_key: str, sys_prompt: str) -> str:
    """
    Call Gemini 1.5 Flash with multi-turn context.
    messages: [{"role": "user"/"assistant", "content": "..."}]
    """
    if not genai:
        return "Gemini SDK not installed (rule mode still works)."
    if not api_key:
        return "No GOOGLE_API_KEY provided (enter in sidebar) or turn off Gemini to use rule mode."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Build context: first message as system prompt, then the history
        full_ctx = [{"role": "user", "parts": [f"[SYSTEM]{sys_prompt}"]}]
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            full_ctx.append({"role": role, "parts": [m["content"]]})

        resp = model.generate_content(full_ctx)
        return (resp.text or "").strip() if hasattr(resp, "text") else "(empty response)"
    except Exception as e:
        return f"Gemini error: {e}"

# -----------------------------
# UI: input + Ask button + Clear
# -----------------------------
st.subheader("Ask about university life")
col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
with col1:
    user_input = st.text_input("Your question", placeholder="e.g., Where is the library?")
with col2:
    ask = st.button("Ask", type="primary", use_container_width=True)

clear = st.button("Clear conversation")
if clear:
    st.session_state.history = []
    st.rerun()

# Submit handling
if ask and user_input.strip():
    st.session_state.history.append({"role": "user", "content": user_input.strip()})

    # 1) Try FAQ first (custom knowledge)
    faq_ans = faq_lookup(user_input)
    if faq_ans:
        answer = f"**From FAQ:**\n{faq_ans}\n\n**TL;DR:** Answered from custom knowledge."
    else:
        # 2) If no FAQ match → optional Gemini; otherwise guidance
        if use_gemini:
            answer = gemini_answer(st.session_state.history, google_api_key, system_prompt)
        else:
            answer = (
                "I couldn't find a direct answer in my campus FAQs.\n"
                "Try rephrasing, or enable **Use Gemini** in the sidebar for AI assistance."
            )

    st.session_state.history.append({"role": "assistant", "content": answer})

# -----------------------------
# Conversation display (stretch)
# -----------------------------
st.divider()
st.subheader("Conversation")
if not st.session_state.history:
    st.info("No messages yet. Ask something above!")
else:
    for m in st.session_state.history:
        if m["role"] == "user":
            st.chat_message("user").markdown(m["content"])
        else:
            st.chat_message("assistant").markdown(m["content"])

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Demo: FAQ-first, optional Gemini fallback, session memory via st.session_state.")
