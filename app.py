import os
import streamlit as st
from dotenv import load_dotenv

# Optional: Gemini SDK (app still runs without it)
try:
    import google.generativeai as genai
except Exception:
    genai = None

# Load .env locally; on Streamlit Cloud use Secrets
load_dotenv()

# ---------- Config ----------
st.set_page_config(page_title="Uni Life Chatbot", page_icon="🎓", layout="centered")
st.title("🎓 Uni Life Chatbot")
st.caption("FAQ-first. Uses Gemini automatically when available. Session history included.")

# Conversation memory
if "history" not in st.session_state:
    st.session_state.history = []  # [{"role": "user"/"assistant", "content": "..."}]

# Read API key (never shown in UI)
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
USE_GEMINI = bool(GOOGLE_API_KEY) and genai is not None  # auto-enable if key + SDK

# System prompt (kept internal)
SYSTEM_PROMPT = (
    "You are a concise, helpful university life assistant. "
    "Use short paragraphs or bullet points. If info may vary by campus, say it. "
    "End with a one-line TL;DR."
)

# ---------- Custom Knowledge (FAQs) ----------
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

# ---------- Gemini ----------
def gemini_answer(messages: list[dict]) -> str:
    """Call Gemini 1.5 Flash with chat history."""
    if not USE_GEMINI:
        return (
            "I couldn't find a direct answer in my campus FAQs."
        )  # Silent fallback message (no key exposure)
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # First message acts as system instruction; then history
        full_ctx = [{"role": "user", "parts": [f"[SYSTEM]{SYSTEM_PROMPT}"]}]
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            full_ctx.append({"role": role, "parts": [m["content"]]})

        resp = model.generate_content(full_ctx)
        return (resp.text or "").strip() if hasattr(resp, "text") else "(empty response)"
    except Exception as e:
        # Do not leak key; return a generic message
        return "I couldn't find a direct answer in my campus FAQs."

# ---------- UI ----------
st.subheader("Ask about university life")
col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
with col1:
    user_input = st.text_input("Your question", placeholder="e.g., Where is the library?")
with col2:
    ask = st.button("Ask", type="primary", use_container_width=True)

if st.button("Clear conversation"):
    st.session_state.history = []
    st.rerun()

# Handle submit
if ask and user_input.strip():
    st.session_state.history.append({"role": "user", "content": user_input.strip()})

    # 1) Try FAQ first
    faq_ans = faq_lookup(user_input)
    if faq_ans:
        answer = f"**From FAQ:**\n{faq_ans}\n\n**TL;DR:** Answered from custom knowledge."
    else:
        # 2) Auto-use Gemini if available; else silent FAQ fallback text
        answer = gemini_answer(st.session_state.history)

    st.session_state.history.append({"role": "assistant", "content": answer})

# Conversation display
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
st.caption("Tip: Keep your FAQ in faqs.txt. Add campus-specific details for better coverage.")
