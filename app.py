import os
import glob
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# ==========================================
# 1. અહીં તમારી Google Gemini API Key મૂકો
# ==========================================
API_KEY = ""

# પેજ સેટઅપ
st.set_page_config(
    page_title="ધોરણ ૩ ગણિત AI શિક્ષક",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 ધોરણ ૩ ગણિત AI ચેટબોટ (મેથ મેલા - સત્ર ૨)")
st.caption("પ્રકરણ ૮ થી ૧૪ | વિદ્યાર્થીઓ, શિક્ષકો અને વાલીઓ માટે સ્ટેપ-બાય-સ્ટેપ ગાણિતિક ઉકેલ")

# API Key ચકાસણી
if API_KEY == "YOUR_GEMINI_API_KEY" or not API_KEY.strip():
    API_KEY = st.sidebar.text_input("🔑 તમારી Gemini API Key અહીં નાખો:", type="password")
    if not API_KEY:
        st.warning("કૃપા કરીને કોડમાં અથવા ડાબી બાજુના બોક્સમાં તમારી Gemini API Key નાખો.")
        st.stop()

client = genai.Client(api_key=API_KEY)

# ==========================================
# 2. સિસ્ટમ સૂચના (System Prompt - RAG & શિક્ષકની ભૂમિકા)
# ==========================================
SYSTEM_PROMPT = """
તમે ગુજરાત બોર્ડ (GCERT) ના ધોરણ ૩ ના ગણિત વિષય ('મેથ મેલા' - બીજું સત્ર, પ્રકરણ ૮ થી ૧૪) ના એક પ્રેમાળ અને નિષ્ણાત શિક્ષક છો.
તમારા જ્ઞાનનો આધાર ફક્ત સાથે જોડેલા GCERT ના અધિકૃત પાઠ્યપુસ્તકો (પ્રકરણ ૮: યોગ્ય ભાગ, પ્રકરણ ૯: સેંકડોનું ઘર-૨, પ્રકરણ ૧૦: વર્ગખંડમાં આનંદ, પ્રકરણ ૧૧: ભરો અને ઉઠાવો, પ્રકરણ ૧૨: આપો અને લો, પ્રકરણ ૧૩: સમય સમયની વાત, પ્રકરણ ૧૪: સુરજકુંડ મેળો) છે.

તમારા નિયમો:
૧. વિદ્યાર્થીઓ, શિક્ષકો અને વાલીઓને એકદમ સરળ, પ્રેમાળ અને શુદ્ધ ગુજરાતી ભાષામાં જવાબ આપો.
૨. દરેક દાખલાનો ઉકેલ તાર્કિક અને સ્ટેપ-બાય-સ્ટેપ (પગલું ૧, પગલું ૨...) સમજાવો જેથી નાનું બાળક પણ જાતે ગણી શકે.
૩. જો વપરાશકર્તા કોઈ દાખલાનો ફોટો (JPG/PNG) કે PDF અપલોડ કરે, તો તેમાંથી રકમ ધ્યાનથી વાંચીને તેનો સચોટ ઉકેલ આપો.
૪. શક્ય હોય ત્યાં કયા પ્રકરણનો દાખલો છે તે પણ જણાવો.
૫. અભ્યાસક્રમ બહારના અઘરા સૂત્રો ન વાપરો; ધોરણ ૩ ના સ્તર મુજબ જ શીખવો.
"""

# ==========================================
# 3. 'books' ફોલ્ડરમાંથી બધી PDF લોડ કરવાનું ફંક્શન
# ==========================================
@st.cache_resource(show_spinner="📚 ધોરણ ૩ ગણિતની ચોપડીઓ લોડ થઈ રહી છે...")
def load_textbooks():
    pdf_files = sorted(glob.glob("books/*.pdf"))
    uploaded_refs = []
    for path in pdf_files:
        uploaded = client.files.upload(file=path)
        uploaded_refs.append(uploaded)
    return uploaded_refs, [os.path.basename(p) for p in pdf_files]

if not os.path.exists("books") or len(glob.glob("books/*.pdf")) == 0:
    st.error("⚠️ 'books' નામનું ફોલ્ડર મળ્યું નથી અથવા તેમાં કોઈ PDF ફાઇલ નથી! કૃપા કરીને 'books' ફોલ્ડરમાં પ્રકરણ ૮ થી ૧૪ ની PDF મૂકો.")
    st.stop()

textbook_refs, loaded_names = load_textbooks()

# સાઈડબારમાં લોડ થયેલી ચોપડીઓ બતાવો

    
with st.sidebar:
    st.subheader("📎 પ્રશ્નનો ફોટો અથવા PDF અપલોડ કરો")
    user_file = st.file_uploader(
        "દાખલાનો ફોટો (JPG/PNG) કે PDF પસંદ કરો:",
        type=["jpg", "jpeg", "png", "pdf"]
    )
    if st.button("🗑️ નવી ચેટ શરૂ કરો"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 4. ચેટ ઈતિહાસ (Chat History)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "નમસ્તે! 🙏 હું તમારો ધોરણ ૩ નો ગણિત શિક્ષક છું. પ્રકરણ ૮ થી ૧૪ માંથી કોઈ પણ દાખલો પૂછો, અથવા ડાબી બાજુથી દાખલાનો **ફોટો / PDF** અપલોડ કરો!"
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 5. યુઝરનો પ્રશ્ન અને AI નો જવાબ
# ==========================================
prompt = st.chat_input("તમારો ગણિતનો પ્રશ્ન અહીં લખો...")

if prompt:
    # યુઝરનો મેસેજ બતાવો
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if user_file is not None:
            st.info(f"📎 જોડેલી ફાઇલ: {user_file.name}")

    # Gemini ને મોકલવાની સામગ્રી તૈયાર કરો (બધી ચોપડીઓ + યુઝર ફાઇલ + પ્રશ્ન)
    contents = list(textbook_refs)

    if user_file is not None:
        if user_file.type in ["image/jpeg", "image/png", "image/jpg"]:
            img = Image.open(user_file)
            contents.append(img)
        elif user_file.type == "application/pdf":
            pdf_part = types.Part.from_bytes(
                data=user_file.getvalue(),
                mime_type="application/pdf"
            )
            contents.append(pdf_part)

    contents.append(prompt)

    # AI જવાબ જનરેટ કરો
   # AI જવાબ જનરેટ કરો (જો એક મોડેલ વ્યસ્ત હોય તો આપોઆપ બીજા પરથી જવાબ લાવશે)
    with st.chat_message("assistant"):
        with st.spinner("🤔 ગણતરી કરી રહ્યો છું..."):
            models_to_try = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
            answer = None
            last_error = None

            for m_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.2
                        )
                    )
                    answer = response.text
                    break
                except Exception as e:
                    last_error = e
                    continue

            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"ભૂલ આવી: {last_error}")