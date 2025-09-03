# 🎓 Uni Life Chatbot (Streamlit)

A tiny chatbot answering questions about university life.  
**Meets assignment requirements**:  
- UI: input box + **Ask** button + display area  
- AI/Logic: FAQ-first, Gemini AI fallback  
- Custom knowledge: ≥5 campus answers (from `faqs.txt`)  
- Conversation history  
- Deployable on **Streamlit Community Cloud**

---

## 🚀 Live Demo
👉 [Click here to try the chatbot](https://uni-chatbot-o6n5kvle7wkedbd8fp7hdv.streamlit.app/)

---

## 🔧 Local Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
