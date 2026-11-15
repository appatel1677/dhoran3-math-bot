import os
import glob
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

# કસ્ટમ CSS વડે દેખાવ વધુ આકર્ષક બનાવવો
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

# વિષયોના બેજ (Badges)
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
# 2. સાઈડબાર (Clean Sidebar & Quick Buttons)
# ==========================================
DEFAULT_API_KEY = ""

with st.sidebar:
    st.header("⚙️ સેટિંગ્સ & વિષયો")
    
    api_key_input = st.text_input(
        "🔑 તમારી Gemini API Key:",
        value=DEFAULT_API_KEY or os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Google AI Studio (aistudio.google.com) માંથી મેળવેલી ફ્રી Gemini API Key અહીં નાખો."
    )

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
        value=True,
        help="જ્યારે કોઈ ભૂલ આવે, ત્યારે સ્ક્રીન પર તેની વિગતવાર ટેકનિકલ માહિતી દર્શાવશે."
    )

    if st.button("🧪 ટેસ્ટ એરર", use_container_width=True):
        st.session_state.test_error = True

if st.session_state.get("test_error", False):
    st.session_state.test_error = False
    if show_error_details:
        st.error("⚠️ ટેસ્ટ એરર: સ્ક્રીન પર એરર ડિસ્પ્લે સિસ્ટમ સક્રિય છે!")
        with st.expander("🔍 એરર વિગતો", expanded=True):
            st.code("RuntimeError: Test Error Triggered\nStatus: Active.", language="python")
    else:
        st.warning("એરર ડિસ્પ્લે બંધ છે. સાઈડબારમાંથી ચાલુ કરો.")

        st.warning("એરર ડિસ્પ્લે સેટિંગ બંધ છે. સાઈડબારમાંથી 'સ્ક્રીન પર એરરની વિગતો બતાવો' ચાલુ કરો.")


# ==========================================
# 3. API Key ચકાસણી અને Gemini Client
# ==========================================
ACTIVE_API_KEY = api_key_input.strip()
if not ACTIVE_API_KEY:
    st.warning("⚠️ કૃપા કરીને ડાબી બાજુના સાઈડબારમાં તમારી **Gemini API Key** દાખલ કરો.")
    st.markdown("""
    > **API Key કેવી રીતે મેળવવી?**
    > 1. [Google AI Studio (aistudio.google.com)](https://aistudio.google.com/app/apikey) પર જાઓ.
    > 2. તમારા Google એકાઉન્ટથી લોગિન કરીને **Create API Key** પર ક્લિક કરો.
    > 3. મળેલી કી ડાબી બાજુના સાઈડબારમાં પેસ્ટ કરો.
    """)
    st.stop()

try:
    client = genai.Client(api_key=ACTIVE_API_KEY)
except Exception as e:
    st.error(f"❌ Gemini Client શરૂ કરવામાં ભૂલ આવી: {e}")
    if show_error_details:
        with st.expander("🔍 એરરની વિગતો (Traceback)", expanded=True):
            st.code(traceback.format_exc(), language="python")
    st.stop()

# ==========================================
# 4. સિસ્ટમ પ્રોમ્પ્ટ (TET-1 ના તમામ વિષયો + વાતચીત)
# ==========================================
SYSTEM_PROMPT = """
તમે ગુજરાત પ્રાથમિક શિક્ષક પાત્રતા કસોટી - ૧ (Gujarat TET-1 Exam: ધોરણ ૧ થી ૫ ના પ્રાથમિક શિક્ષક માટે) ના એક નિષ્ણાત, સ્નેહાળ, ધીરજવાન અને પ્રોત્સાહક AI શિક્ષક તથા માર્ગદર્શક છો.

તમારે TET-1 ના નીચે મુજબના તમામ વિષયોમાં સંપૂર્ણ, સચોટ અને વિગતવાર માર્ગદર્શન આપવાનું છે:

૧. બાળ વિકાસ અને શિક્ષણના સિદ્ધાંતો (Child Development & Pedagogy / બાળ મનોવિજ્ઞાન):
   - બાળ મનોવિજ્ઞાન, બાળકના શારીરિક, માનસિક, સામાજિક અને આવેગિક વિકાસના તબક્કા.
   - પ્રખ્યાત મનોવૈજ્ઞાનિકોના સિદ્ધાંતો: જીન પિયાજે (Piaget), લેવ વાયગોત્સ્કી (Vygotsky), લોરેન્સ કોહલબર્ગ (Kohlberg), સ્કિનર (Skinner), થોર્નડાઇક (Thorndike), પાવલોવ (Pavlov) વગેરે.
   - અધ્યયન-અધ્યાપન પદ્ધતિઓ, સમાવેશી શિક્ષણ (Inclusive Education), મૂલ્યાંકન અને માપન (CCE).
   - રાષ્ટ્રીય શિક્ષણ નીતિ (NEP 2020), શિક્ષાનો અધિકાર કાયદો (RTE 2009).

૨. ગુજરાતી ભાષા અને વ્યાકરણ (Gujarati Language & Grammar):
   - સંપૂર્ણ ગુજરાતી વ્યાકરણ: જોડણીના નિયમો, સંધિ, સમાસ, અલંકાર, છંદ, કૃદંત, નિપાત, વિભક્તિ, વાક્યના પ્રકાર (કર્તરિ, કર્મણિ, ભાવે, પ્રેરક).
   - શબ્દભંડોળ: સમાનાર્થી શબ્દો, વિરુદ્ધાર્થી શબ્દો, રૂઢિપ્રયોગો, કહેવતો, શબ્દસમૂહ માટે એક શબ્દ, તળપદા શબ્દો.
   - ગુજરાતી સાહિત્ય, જાણીતા કવિઓ, લેખકો, તેમની કૃતિઓ અને ઉપનામો.

૩. અંગ્રેજી ભાષા અને વ્યાકરણ (English Language & Grammar):
   - Parts of Speech (Noun, Pronoun, Verb, Adverb, Adjective, Preposition, Conjunction).
   - Tenses (કાળ), Active & Passive Voice, Direct & Indirect Speech.
   - Articles (A, An, The), Degree of Comparison, Question Tags.
   - Vocabulary, Synonyms, Antonyms, Idioms & Phrases, Spelling rules.
   - ગુજરાતી માધ્યમના ઉમેદવારો સરળતાથી સમજી શકે તે માટે અંગ્રેજી નિયમો ગુજરાતીમાં સરળતાથી સમજાવવા.

૪. ગણિત (Mathematics):
   - સંખ્યા જ્ઞાન, સ્થાનકિંમત, મૂળભૂત ક્રિયાઓ (સરવાળો, બાદબાકી, ગુણાકાર, ભાગાકાર).
   - અપૂર્ણાંક, દશાંશ સંખ્યાઓ, લ.સા.અ. અને ગુ.સા.અ. (LCM & HCF).
   - ટકાવારી (Percentage), નફો-ખોટ (Profit & Loss), સાદું વ્યાજ (Simple Interest).
   - ગુણોત્તર અને પ્રમાણ (Ratio & Proportion), સરેરાશ (Average), સમય અને કાર્ય (Time & Work).
   - ભૂમિતિ: આકારો, ક્ષેત્રફળ, પરિમિતિ, ઘનફળ અને કોયડાઓ.
   - દરેક દાખલો સ્ટેપ-બાય-સ્ટેપ (પગલું ૧, પગલું ૨...) ગણીને સમજાવો અને પરીક્ષા માટે ઉપયોગી શોર્ટકટ ટ્રીક પણ જણાવો.

૫. પર્યાવરણ, વિજ્ઞાન અને સામાન્ય જ્ઞાન (Environmental Studies, Science & GK):
   - પર્યાવરણ શિક્ષણ (EVS), આપણી પૃથ્વી, જળ, વાયુ, જમીન, પ્રદૂષણ, સંરક્ષણ.
   - પ્રાથમિક વિજ્ઞાન: માનવ શરીર, પોષણ, રોગો, વનસ્પતિ અને પ્રાણી જગત.
   - સામાજિક વિજ્ઞાન: ગુજરાતનો ઇતિહાસ, ભૂગોળ, સાંસ્કૃતિક વારસો, મેળાઓ, જિલ્લાઓ.
   - ભારતીય બંધારણના પાયાના ખ્યાલો, સામાન્ય જ્ઞાન (GK) અને સમકાલીન ઘટનાઓ.

૬. સામાન્ય વાતચીત અને શુભેચ્છાઓ (General Conversation):
   - જો વપરાશકર્તા 'Hello', 'Hi', 'નમસ્તે', 'કેમ છો', 'Good Morning' જેવા શુભેચ્છા સંદેશા મોકલે, તો ખૂબ જ પ્રેમાળ, પ્રોત્સાહક અને ઉત્સાહપૂર્વક સ્વાગત કરો.
   - TET-1 પરીક્ષાની તૈયારી કેવી રીતે કરવી, અભ્યાસનું આયોજન, ટાઈમ ટેબલ, અને આત્મવિશ્વાસ વધારતી પ્રેરણાદાયી સલાહ આપો.

તમારા જવાબ આપવાના નિયમો:
- હંમેશા શુદ્ધ, સન્માનજનક, સ્પષ્ટ અને પ્રોત્સાહક ગુજરાતી ભાષામાં જવાબ આપો.
- જો વપરાશકર્તા કોઈ પ્રશ્નપત્ર, ફોટો કે PDF અપલોડ કરે, તો તેમાંથી પ્રશ્ન ધ્યાનપૂર્વક વાંચીને ચોક્કસ સાચો જવાબ અને તેનું સચોટ કારણ સમજાવો.
- જો પ્રશ્ન MCQ પ્રકારનો હોય, તો સાચો વિકલ્પ સ્પષ્ટ જણાવો અને અન્ય વિકલ્પો શા માટે અયોગ્ય છે તેની ટૂંકી સ્પષ્ટતા આપો.
"""

# ==========================================
# 5. ચેટ ઈતિહાસ અને પ્રશ્નોત્તરી (Chat History & UI)
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

👉 તમે કોઈ પણ વિષયનો પ્રશ્ન પૂછી શકો છો, સામાન્ય વાતચીત (જેમ કે **'Hello'**) કરી શકો છો, અથવા ડાબી બાજુથી પ્રશ્નપત્ર/દાખલાનો **ફોટો કે PDF** અપલોડ કરી શકો છો!"""
        }
    ]

# અગાઉના તમામ મેસેજ સ્ક્રીન પર દર્શાવવા
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 6. યુઝરનો પ્રશ્ન અને AI નો જવાબ
# ==========================================
prompt = st.chat_input("TET-1 નો કોઈ પણ પ્રશ્ન પૂછો અથવા 'Hello' લખો...", accept_file=True)

if prompt:
    # prompt is either an object or a dict or a ChatInputResult containing text and files in Streamlit >= 1.41+
    # Let's handle both string/object safely according to Streamlit accept_file=True API
    user_text = getattr(prompt, "text", str(prompt))
    user_files = getattr(prompt, "files", None)

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
        if user_files:
            for uf in user_files:
                st.info(f"📎 જોડેલી ફાઇલ: {uf.name}")

    with st.chat_message("assistant"):
        with st.spinner("🤔 વિચારી રહ્યો છું અને ઉત્તર તૈયાર કરી રહ્યો છું..."):
            
            models_to_try = ["gemini-flash-lite-latest", "gemini-3.8-flash-lite"]

            answer = None
            errors_occurred = []
            current_user_parts = []
            file_error = None

            if user_files:
                for uf in user_files:
                    try:
                        file_bytes = uf.getvalue()
                        mime = uf.type
                        if not mime:
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
                        file_error = str(fe)
                        errors_occurred.append(f"ફાઇલ પ્રોસેસિંગ એરર: {str(fe)}")

            current_user_parts.append(types.Part.from_text(text=user_text))

            contents = []
            recent_msgs = st.session_state.messages[:-1]
            if len(recent_msgs) > 6:
                recent_msgs = recent_msgs[-6:]

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
                    else:
                        errors_occurred.append(f"[{m_name}] મોડેલ તરફથી ખાલી જવાબ મળ્યો.")
                except Exception as e:
                    errors_occurred.append(f"[{m_name}] નિષ્ફળ: {str(e)}")
                    continue

            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("❌ ક્ષમા કરશો! તમારા પ્રશ્નનો જવાબ મેળવવામાં એરર આવી છે.")
                
                if show_error_details:
                    with st.expander("🔍 સ્ક્રીન પર એરરની વિગતવાર માહિતી (Detailed Error Report)", expanded=True):
                        st.markdown("### ⚠️ ટેકનિકલ એરર લોગ:")
                        for err in errors_occurred:
                            st.write(f"- `{err}`")
                        
                        if file_error:
                            st.markdown("### 📎 ફાઇલ પ્રોસેસિંગ એરર:")
                            st.code(file_error)

                        st.markdown("### 🛠️ સમસ્યા નિવારણ (Troubleshooting Guide):")
                        st.markdown("""
                        1. **API Key ચકાસો:** ખાતરી કરો કે દાખલ કરેલી Gemini API Key સાચી અને સક્રિય છે.
                        2. **ક્વોટા / રેટ લિમિટ:** ગૂગલ ફ્રી API ની વિનંતી મર્યાદા (Rate Limit) પૂરી થઈ ગઈ હોય તો ૧ મિનિટ પછી ફરી પ્રયાસ કરો.
                        3. **મોડેલ બદલો:** સાઈડબારમાંથી બીજું મોડેલ પસંદ કરીને ફરી સવાલ પૂછો.
                        4. **ઇન્ટરનેટ કનેક્શન:** તમારું ઇન્ટરનેટ કનેક્શન સક્રિય છે તેની ખાતરી કરો.
                        """)
                else:
                    st.info("💡 વધુ વિગતવાર એરર જોવા માટે સાઈડબારમાં 'સ્ક્રીન પર એરરની વિગતો બતાવો' વિકલ્પ ચાલુ કરો.")
