# 🎓 Uni Life Chatbot (Streamlit)

A tiny chatbot answering questions about university life.  
**Meets assignment requirements**:  
- UI: input box + **Ask** button + display area  
- AI/Logic: rule-based FAQ, optional Gemini fallback  
- Custom knowledge: ≥5 campus answers (from `faqs.txt`)  
- Stretch: shows **conversation history** in-session  
- Deployable on **Streamlit Community Cloud** (free)

## 🔧 Local Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
