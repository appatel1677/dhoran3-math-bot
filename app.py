import os
import traceback
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. પેજ સેટઅપ અને રૂપરેખા (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="🎓 ગુજરાત TET-1 AI શિક્ષક",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #2563EB;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .subject-pill {
        display: inline-block;
        background-color: #EEF2FF;
        color: #3730A3;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.88rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.4rem;
        border: 1px solid #C7D2FE;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎓 ગુજરાત TET-1 AI શિક્ષક</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">બાળ વિકાસ અને મનોવિજ્ઞાન, ગુજરાતી, અંગ્રેજી, ગણિત અને પર્યાવરણ | સ્માર્ટ પરીક્ષા સહાયક</div>', unsafe_allow_html=True)

st.markdown("""
<div>
    <span class="subject-pill">🧠 બાળ વિકાસ અને મનોવિજ્ઞાન</span>
    <span class="subject-pill">📖 ગુજરાતી વ્યાકરણ</span>
    <span class="subject-pill">🔤 અંગ્રેજી વ્યાકરણ</span>
    <span class="subject-pill">🔢 ગણિત કોયડા</span>
    <span class="subject-pill">🌍 પર્યાવરણ & GK</span>
    <span class="subject-pill">💬 સામાન્ય વાતચીત ('Hello')</span>
</div>
""", unsafe_allow_html=True)
st.write("---")

# ==========================================
# 2. ઓટોમેટિક API Key મેળવવી (Secrets / Env માંથી)
# ==========================================
SECRET_API_KEY = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        SECRET_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not SECRET_API_KEY:
    SECRET_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ==========================================
# 3. સાઈડબાર (Clean Sidebar & Quick Buttons)
# ==========================================
with st.sidebar:
    st.header("⚙️ સેટિંગ્સ & વિષયો")
    
    # જો Secrets માં કી સેવ હશે, તો યુઝરને વારેઘડીએ કી નહીં પૂછે!
    if SECRET_API_KEY:
        ACTIVE_API_KEY = SECRET_API_KEY.strip()
        st.success("✅ AI શિક્ષક કનેક્ટેડ છે!")
    else:
        api_key_input = st.text_input(
            "🔑 તમારી Gemini API Key:",
            value="",
            type="password",
            help="Google AI Studio (aistudio.google.com) માંથી મેળવેલી ફ્રી Gemini API Key અહીં નાખો."
        )
        ACTIVE_API_KEY = api_key_input.strip()

    if st.button("🔄 નવી ચેટ શરૂ કરો", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("💡 વિષયવાર ક્વિક પ્રશ્નો")
    
    if st.button("📝 મનોવિજ્ઞાન MCQ", use_container_width=True):
        st.session_state.pending_prompt = "બાળ મનોવિજ્ઞાન અને શિક્ષણશાસ્ત્ર (Pedagogy) ના મહત્વના ૫ MCQs તેમની વિગતવાર સમજૂતી સાથે આપો."
        st.rerun()

    if st.button("📚 ગુજરાતી વ્યાકરણ", use_container_width=True):
        st.session_state.pending_prompt = "TET-1 પરીક્ષા માટે ગુજરાતી વ્યાકરણના મુખ્ય નિયમો (સંધિ, સમાસ, અલંકાર) ઉદાહરણ સાથે આપો."
        st.rerun()

    if st.button("🔤 અંગ્રેજી વ્યાકરણ", use_container_width=True):
        st.session_state.pending_prompt = "TET-1 પરીક્ષા માટે English Grammar (Tenses, Articles, Prepositions) ના અગત્યના નિયમો ગુજરાતીમાં સમજાવો."
        st.rerun()

    if st.button("🔢 ગણિત કોયડા", use_container_width=True):
        st.session_state.pending_prompt = "TET-1 પરીક્ષા માટે ગણિતના અગત્યના પ્રશ્નો અને તેના ઉકેલ માટેની શોર્ટકટ ટ્રીક્સ સમજાવો."
        st.rerun()

    if st.button("🌍 પર્યાવરણ અને GK", use_container_width=True):
        st.session_state.pending_prompt = "પર્યાવરણ, સામાન્ય જ્ઞાન (GK) અને સામાજિક વિજ્ઞાનના TET-1 માટેના મુખ્ય પ્રશ્નો આપો."
        st.rerun()

    st.markdown("---")
    show_error_details = st.checkbox(
        "🐞 સ્ક્રીન પર એરરની વિગતો બતાવો",
        value=True
    )

# ==========================================
# 4. API Key ચકાસણી અને Gemini Client
# ==========================================
if not ACTIVE_API_KEY:
    st.warning("⚠️ કૃપા કરીને ડાબી બાજુના સાઈડબારમાં તમારી **Gemini API Key** દાખલ કરો.")
    st.stop()

try:
    client = genai.Client(api_key=ACTIVE_API_KEY)
except Exception as e:
    st.error(f"❌ Gemini Client શરૂ કરવામાં ભૂલ આવી: {e}")
    st.stop()

@st.cache_data(ttl=3600)
def get_available_gemini_models(api_key):
    temp_client = genai.Client(api_key=api_key)
    valid_models = []
    try:
        for m in temp_client.models.list():
            name = m.name.replace("models/", "")
            if "gemini" in name and ("flash" in name or "pro" in name):
                if not any(x in name for x in ["vision", "embedding", "aqa", "imagen", "veo", "audio", "tts"]):
                    valid_models.append(name)
    except Exception:
        pass
    
    priority = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    ordered = [p for p in priority if p in valid_models]
    for v in valid_models:
        if v not in ordered:
            ordered.append(v)
            
    return ordered if ordered else priority

# ==========================================
# 5. સિસ્ટમ પ્રોમ્પ્ટ
# ==========================================
SYSTEM_PROMPT = """
તમે ગુજરાત પ્રાથમિક શિક્ષક પાત્રતા કસોટી - ૧ (Gujarat TET-1 Exam: ધોરણ ૧ થી ૫ ના પ્રાથમિક શિક્ષક માટે) ના એક નિષ્ણાત, સ્નેહાળ, ધીરજવાન અને પ્રોત્સાહક AI શિક્ષક તથા માર્ગદર્શક છો.
તમારે TET-1 ના તમામ વિષયો (બાળ વિકાસ અને મનોવિજ્ઞાન, ગુજરાતી, અંગ્રેજી, ગણિત, પર્યાવરણ & GK) માં સંપૂર્ણ, સચોટ અને વિગતવાર માર્ગદર્શન આપવાનું છે.
હંમેશા શુદ્ધ, સ્પષ્ટ અને પ્રોત્સાહક ગુજરાતી ભાષામાં જવાબ આપો. જો વપરાશકર્તા 'Hello' કે 'Hi' લખે તો પ્રેમાળ સ્વાગત કરો.
"""

# ==========================================
# 6. ચેટ ઈતિહાસ અને પ્રશ્નોત્તરી
# ==========================================
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """નમસ્તે! 🙏 હું તમારો **ગુજરાત TET-1 AI શિક્ષક અને માર્ગદર્શક** છું.

હું તમને પ્રાથમિક શિક્ષક પાત્રતા કસોટી (TET-1) ના નીચેના તમામ વિષયોમાં સંપૂર્ણ મદદ કરવા માટે ઉપલબ્ધ છું:
- 🧠 **બાળ વિકાસ અને મનોવિજ્ઞાન**
- 📖 **ગુજરાતી ભાષા અને વ્યાકરણ**
- 🔤 **અંગ્રેજી ભાષા અને વ્યાકરણ (English Grammar)**
- 🔢 **ગણિત (સ્ટેપ-બાય-સ્ટેપ ઉકેલ અને શોર્ટકટ ટ્રીક્સ)**
- 🌍 **પર્યાવરણ, સામાજિક વિજ્ઞાન અને સામાન્ય જ્ઞાન (EVS & GK)**

👉 તમે કોઈ પણ વિષયનો પ્રશ્ન પૂછી શકો છો, સામાન્ય વાતચીત (જેમ કે **'Hello'**) કરી શકો છો, અથવા `+` પર ક્લિક કરીને પ્રશ્નપત્ર/દાખલાનો **ફોટો કે PDF** અપલોડ કરી શકો છો!"""
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 7. યુઝરનો પ્રશ્ન અને AI નો જવાબ
# ==========================================
chat_input_val = st.chat_input("TET-1 નો કોઈ પણ પ્રશ્ન પૂછો અથવા 'Hello' લખો...", accept_file=True)

user_text = None
user_files = None

if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    user_text = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
elif chat_input_val:
    user_text = getattr(chat_input_val, "text", str(chat_input_val))
    user_files = getattr(chat_input_val, "files", None)

if user_text or user_files:
    display_text = user_text if user_text else "📎 અપલોડ કરેલી ફાઇલ સમજાવો."
    st.session_state.messages.append({"role": "user", "content": display_text})
    
    with st.chat_message("user"):
        st.markdown(display_text)
        if user_files:
            for uf in user_files:
                st.info(f"📎 જોડેલી ફાઇલ: {uf.name}")

    with st.chat_message("assistant"):
        with st.spinner("🤔 વિચારી રહ્યો છું અને ઉત્તર તૈયાર કરી રહ્યો છું..."):
            models_to_try = get_available_gemini_models(ACTIVE_API_KEY)
            answer = None
            errors_occurred = []
            current_user_parts = []

            if user_files:
                for uf in user_files:
                    try:
                        file_bytes = uf.getvalue()
                        mime = uf.type or "application/octet-stream"
                        if uf.name.lower().endswith(".pdf"):
                            mime = "application/pdf"
                        elif uf.name.lower().endswith((".jpg", ".jpeg")):
                            mime = "image/jpeg"
                        elif uf.name.lower().endswith(".png"):
                            mime = "image/png"
                        
                        current_user_parts.append(
                            types.Part.from_bytes(data=file_bytes, mime_type=mime)
                        )
                    except Exception as fe:
                        errors_occurred.append(f"ફાઇલ પ્રોસેસિંગ એરર: {str(fe)}")

            current_user_parts.append(types.Part.from_text(text=display_text))

            contents = []
            recent_msgs = st.session_state.messages[:-1][-6:]
            for m in recent_msgs:
                role = "user" if m["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=m["content"])]
                    )
                )
            contents.append(types.Content(role="user", parts=current_user_parts))

            for m_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.3
                        )
                    )
                    if response and response.text:
                        answer = response.text
                        break
                except Exception as e:
                    errors_occurred.append(f"[{m_name}] નિષ્ફળ: {str(e)}")
                    continue

            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("❌ ક્ષમા કરશો! તમારા પ્રશ્નનો જવાબ મેળવવામાં એરર આવી છે.")
                if show_error_details:
                    with st.expander("🔍 સ્ક્રીન પર એરરની વિગતવાર માહિતી", expanded=True):
                        for err in errors_occurred:
                            st.write(f"- `{err}`")