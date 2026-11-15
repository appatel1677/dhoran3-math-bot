import os
import traceback
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. પેજ સેટઅપ અને રૂપરેખા (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="🎓 ગુજરાત TET-1 & TET-2 AI શિક્ષક",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.02rem;
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
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.4rem;
        border: 1px solid #C7D2FE;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎓 ગુજરાત TET-1 & TET-2 AI શિક્ષક</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">ધોરણ ૧ થી ૫ (TET-1) અને ધોરણ ૬ થી ૮ (TET-2: સામાજિક વિજ્ઞાન / ગણિત-વિજ્ઞાન / ભાષા) | સ્માર્ટ પરીક્ષા સહાયક</div>', unsafe_allow_html=True)

st.markdown("""
<div>
    <span class="subject-pill">🧠 બાળ મનોવિજ્ઞાન</span>
    <span class="subject-pill">📖 ગુજરાતી</span>
    <span class="subject-pill">🔤 અંગ્રેજી</span>
    <span class="subject-pill">🔢 ગણિત-વિજ્ઞાન</span>
    <span class="subject-pill">🌍 પર્યાવરણ & સા.વિજ્ઞાન</span>
    <span class="subject-pill">📰 Current Affairs</span>
    <span class="subject-pill">📜 NEP 2020 & GCERT</span>
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
# 3. સાઈડબાર (Exam Mode + Quick Buttons)
# ==========================================
with st.sidebar:
    st.header("⚙️ પરીક્ષા અને સેટિંગ્સ")

    if SECRET_API_KEY:
        ACTIVE_API_KEY = SECRET_API_KEY.strip()
        st.success("✅ AI શિક્ષક કનેક્ટેડ છે!")
    else:
        api_key_input = st.text_input(
            "🔑 તમારી Gemini API Key:",
            value="",
            type="password",
            help="Google AI Studio માંથી મેળવેલી Gemini API Key અહીં નાખો."
        )
        ACTIVE_API_KEY = api_key_input.strip()

    # પરીક્ષા પસંદગી (TET-1 અથવા TET-2)
    exam_mode = st.selectbox(
        "🎯 પરીક્ષાનો વિભાગ પસંદ કરો:",
        [
            "TET-1 (ધોરણ ૧ થી ૫)",
            "TET-2 (ધોરણ ૬ થી ૮ - સામાજિક વિજ્ઞાન)",
            "TET-2 (ધોરણ ૬ થી ૮ - ગણિત અને વિજ્ઞાન)",
            "TET-2 (ધોરણ ૬ થી ૮ - ભાષા: ગુજરાતી/અંગ્રેજી/હિન્દી/સંસ્કૃત)"
        ]
    )

    if st.button("🔄 નવી ચેટ શરૂ કરો", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("🚀 સ્માર્ટ ફીચર્સ & Current Affairs")

    if st.button("📰 તાજા Current Affairs", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} પરીક્ષા માટે છેલ્લા ૧ મહિનાના સૌથી મહત્વના ૫ Current Affairs (ગુજરાત, ભારત, શિક્ષણલક્ષી યોજનાઓ, રમતગમત અને પુરસ્કારો) MCQ અને તેની સમજૂતી સાથે આપો."
        st.rerun()

    if st.button("📝 મિની મોક ટેસ્ટ (૧૦ MCQs)", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} ના સંપૂર્ણ અભ્યાસક્રમ મુજબ મિશ્ર વિષયોના ૧૦ મહત્વના MCQs આપો. પહેલા બધા પ્રશ્નો આપો અને અંતે 'જવાબવહી (Answer Key)' ટૂંકી સમજૂતી સાથે આપો."
        st.rerun()

    if st.button("📜 NEP 2020 & RTE 2009", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} માટે રાષ્ટ્રીય શિક્ષણ નીતિ (NEP 2020), શિક્ષણનો અધિકાર કાયદો (RTE 2009) અને NCF 2023 ના મુખ્ય મુદ્દાઓ અને સંભવિત પ્રશ્નો સમજાવો."
        st.rerun()

    if st.button("📚 GCERT પાઠ્યપુસ્તક સારાંશ", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} માટે ગુજરાત સરકારના GCERT પાઠ્યપુસ્તકો (ધોરણ ૩ થી ૮) ના સૌથી મહત્વના ૧૫ વન-લાઇનર પ્રશ્નો અને જવાબો આપો."
        st.rerun()

    if st.button("🗣️ શબ્દભંડોળ & કહેવતો", use_container_width=True):
        st.session_state.pending_prompt = "TET-1 અને TET-2 માટે ગુજરાતીના ૫ મહત્વના રૂઢિપ્રયોગો, ૫ કહેવતો, ૫ શબ્દસમૂહ માટે એક શબ્દ અને અંગ્રેજીના ૫ અગત્યના Idioms/Synonyms ગુજરાતી અર્થ સાથે આપો."
        st.rerun()

    if st.button("🗓️ અભ્યાસનું ટાઈમ-ટેબલ", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} ની સંપૂર્ણ તૈયારી માટે ૩૦ દિવસનું સ્માર્ટ અભ્યાસ આયોજન (Study Time-Table) અને પાસ થવાની વ્યૂહરચના બનાવી આપો."
        st.rerun()

    st.markdown("---")
    st.subheader("📖 વિષયવાર ક્વિક પ્રશ્નો")

    if st.button("🧠 મનોવિજ્ઞાન (Pedagogy)", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} માટે બાળ મનોવિજ્ઞાન અને શિક્ષણશાસ્ત્ર (Pedagogy) ના મહત્વના ૫ MCQs તેમની વિગતવાર સમજૂતી સાથે આપો."
        st.rerun()

    if st.button("📖 ગુજરાતી વ્યાકરણ", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} પરીક્ષા માટે ગુજરાતી વ્યાકરણ (સંધિ, સમાસ, અલંકાર, છંદ, કૃદંત) ના મુખ્ય નિયમો ઉદાહરણ સાથે આપો."
        st.rerun()

    if st.button("🔤 અંગ્રેજી વ્યાકરણ", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} પરીક્ષા માટે English Grammar (Tenses, Active-Passive, Direct-Indirect, Articles, Prepositions) ના નિયમો ગુજરાતીમાં સમજાવો."
        st.rerun()

    if st.button("🔢 ગણિત & વિજ્ઞાન", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} પરીક્ષા માટે ગણિતના અગત્યના દાખલા (શોર્ટકટ ટ્રીક્સ સાથે) અને સામાન્ય વિજ્ઞાનના મુખ્ય પ્રશ્નો સમજાવો."
        st.rerun()

    if st.button("🌍 પર્યાવરણ & સા. વિજ્ઞાન", use_container_width=True):
        st.session_state.pending_prompt = f"{exam_mode} પરીક્ષા માટે પર્યાવરણ (EVS), સામાજિક વિજ્ઞાન (ઇતિહાસ, ભૂગળ, બંધારણ) અને ગુજરાત GK ના મુખ્ય પ્રશ્નો આપો."
        st.rerun()

    st.markdown("---")
    enable_live_search = st.checkbox(
        "🌐 લાઈવ Google Search (Current Affairs માટે)",
        value=True,
        help="આ ચાલુ રાખવાથી AI તાજા સમાચાર અને Current Affairs ઇન્ટરનેટ પરથી શોધીને આપશે."
    )
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
        "gemini-1.5-pro"
    ]
    ordered = [p for p in priority if p in valid_models]
    for v in valid_models:
        if v not in ordered:
            ordered.append(v)
            
    return ordered if ordered else priority

# ==========================================
# 5. સિસ્ટમ પ્રોમ્પ્ટ (TET-1 & TET-2 સંપૂર્ણ માર્ગદર્શક)
# ==========================================
SYSTEM_PROMPT = f"""
તમે ગુજરાત પ્રાથમિક શિક્ષક પાત્રતા કસોટી - ૧ અને ૨ (Gujarat TET-1: ધોરણ ૧ થી ૫ અને TET-2: ધોરણ ૬ થી ૮) ના નિષ્ણાત, સ્નેહાળ અને પ્રોત્સાહક AI શિક્ષક છો.
હાલમાં વપરાશકર્તાએ **{exam_mode}** પસંદ કરેલ છે, તેથી જવાબો તે મુજબના સ્તર (Level) ને ધ્યાનમાં રાખીને આપવા.

તમારા મુખ્ય વિષયો અને જવાબદારીઓ:
૧. **બાળ વિકાસ અને શિક્ષણના સિદ્ધાંતો (Pedagogy):** વિકાસના તબક્કા, પિયાજે, વાયગોત્સ્કી, કોહલબર્ગ, સ્કિનર, પાવલોવ, થોર્નડાઇક, સમાવેશી શિક્ષણ, CCE, NEP 2020 અને RTE 2009.
૨. **ગુજરાતી ભાષા અને સાહિત્ય:** જોડણી, સંધિ, સમાસ, અલંકાર, છંદ, કૃદંત, નિપાત, વિભક્તિ, રૂઢિપ્રયોગો, કહેવતો, કવિઓ-લેખકો અને તેમની કૃતિઓ.
૩. **અંગ્રેજી ભાષા અને વ્યાકરણ:** Parts of Speech, Tenses, Active-Passive, Direct-Indirect, Articles, Degree, Question Tags, Vocabulary (ગુજરાતી માધ્યમના વિદ્યાર્થીઓને સરળતાથી સમજાય તેમ સમજાવવું).
૪. **ગણિત અને વિજ્ઞાન (TET-1 & TET-2 Math-Science):** સંખ્યા જ્ઞાન, ટકાવારી, નફો-ખોટ, વ્યાજ, ગુણોત્તર, બીજગણિત, ભૂમિતિ (સ્ટેપ-બાય-સ્ટેપ ઉકેલ અને શોર્ટકટ ટ્રીક્સ સાથે), તથા ધોરણ ૬ થી ૮ GCERT વિજ્ઞાન (ભૌતિક, રસાયણ, જીવવિજ્ઞાન).
૫. **પર્યાવરણ અને સામાજિક વિજ્ઞાન (TET-1 EVS & TET-2 Social Science):** ધોરણ ૩ થી ૮ GCERT પર્યાવરણ, ઇતિહાસ, ભૂગોળ, નાગરિકશાસ્ત્ર, ભારતીય બંધારણ, ગુજરાતનો સાંસ્કૃતિક વારસો.
૬. **વર્તમાન પ્રવાહો (Current Affairs):** ગુજરાત અને ભારતની તાજી ઘટનાઓ, શિક્ષણલક્ષી યોજનાઓ, પુરસ્કારો, રમતગમત અને મહત્વની નિયુક્તિઓ.
૭. **સામાન્ય વાતચીત:** 'Hello', 'Hi', 'નમસ્તે' જેવા સંદેશાનો પ્રેમાળ અને પ્રોત્સાહક જવાબ આપવો.

નિયમો:
- હંમેશા શુદ્ધ, સ્પષ્ટ અને પ્રોત્સાહક ગુજરાતી ભાષામાં જવાબ આપો.
- જો ફોટો કે PDF અપલોડ થાય, તો તેમાંથી પ્રશ્ન વાંચીને ચોક્કસ ઉકેલ સમજાવો.
"""

# ==========================================
# 6. ચેટ ઈતિહાસ અને પ્રશ્નોત્તરી
# ==========================================
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """નમસ્તે! 🙏 હું તમારો **ગુજરાત TET-1 & TET-2 AI શિક્ષક** છું.

હવે આ એપમાં **ધોરણ ૧ થી ૫ (TET-1)** અને **ધોરણ ૬ થી ૮ (TET-2: સામાજિક વિજ્ઞાન, ગણિત-વિજ્ઞાન, ભાષા)** બંનેની સંપૂર્ણ તૈયારી ઉપલબ્ધ છે:
- 📰 **લાઈવ Current Affairs** (તાજા સમાચાર અને યોજનાઓ)
- 📝 **મિની મોક ટેસ્ટ** (૧૦ MCQs પ્રેક્ટિસ)
- 📜 **NEP 2020, RTE 2009 & GCERT પાઠ્યપુસ્તક સારાંશ**
- 🧠 **બાળ મનોવિજ્ઞાન, ગુજરાતી, અંગ્રેજી, ગણિત-વિજ્ઞાન અને સામાજિક વિજ્ઞાન**

👉 ડાબી બાજુથી તમારી પરીક્ષા (**TET-1** કે **TET-2**) પસંદ કરો, કોઈ બટન દબાવો અથવા નીચે તમારો પ્રશ્ન લખો / ફોટો અપલોડ કરો!"""
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 7. યુઝરનો પ્રશ્ન અને AI નો જવાબ
# ==========================================
chat_input_val = st.chat_input("TET-1 કે TET-2 નો કોઈ પણ પ્રશ્ન પૂછો અથવા 'Hello' લખો...", accept_file=True)

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

            # લાઈવ Google Search ટૂલ સેટિંગ
            search_tools = [{"google_search": {}}] if enable_live_search else None

            for m_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.3,
                            tools=search_tools
                        )
                    )
                    if response and response.text:
                        answer = response.text
                        break
                except Exception as e:
                    # જો કોઈ જૂના મોડેલમાં google_search સપોર્ટ ન હોય તો તેના વગર ફરી પ્રયાસ કરવો
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
                    except Exception as e2:
                        errors_occurred.append(f"[{m_name}] નિષ્ફળ: {str(e2)}")
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