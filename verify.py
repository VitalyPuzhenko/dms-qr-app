import streamlit as st
import io, qrcode
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ---------------- CONFIG ----------------
SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID", "")
SHEET_RANGE = st.secrets.get("SHEET_RANGE", "A1:E1")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_INFO = st.secrets.get("GOOGLE_CREDENTIALS", None)
BASE_URL = "https://vitalypuzhenko-dms-qr-app.streamlit.app"

# ---------------- GOOGLE SHEETS ----------------
@st.cache_resource
def get_gsheets_service():
    creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Перевірка документа", page_icon="✅", layout="centered")
st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 700px;}
        h1, h2, h3, h4 {text-align: center;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔍 Перевірка документа")

# ---------------- MAIN LOGIC ----------------
query_params = st.experimental_get_query_params()

if "doc" in query_params:
    doc_id = query_params["doc"][0]
    st.info(f"Перевірка документа ID: `{doc_id}`")

    service = get_gsheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE
    ).execute()
    rows = result.get("values", [])
    match = next((r for r in rows if r[0] == doc_id), None)

    if match:
        st.success("✅ Документ підтверджено в журналі підписів")
        st.markdown("### 📄 Реквізити")
        st.write(f"**ID документа:** `{match[0]}`")
        st.write(f"**Підписант:** {match[2]}")
        st.write(f"**Дата:** {match[3]}")
        st.write(f"**Хеш (SHA256):** `{match[1]}`")

        qr_buf = io.BytesIO()
        qrcode.make(f"{BASE_URL}/?doc={match[0]}").save(qr_buf, format="PNG")
        st.image(qr_buf.getvalue(), width=120, caption="QR для перевірки")

        st.markdown("---")
        st.markdown("#### 🖋️ Електронний підпис:")
        st.code(match[4] if len(match) > 4 else "—", language="text")
    else:
        st.error("❌ Документ не знайдено у журналі.")
else:
    st.write("Використайте посилання з QR-коду:")
    st.code(f"{BASE_URL}/?doc=<a6cbe37b-1ba4-4050-84a3-6eff34719b83>")
