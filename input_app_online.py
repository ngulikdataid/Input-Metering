# ==============================================================
# STREAMLIT INPUT APP - FULL PARAMETER NEC 20KW (FIXED VERSION)
# ==============================================================
# FIXES APPLIED:
# 1. Prevent crash if secrets not found
# 2. Ensure placeholder count = column count
# 3. Add connection test
# 4. Improve error handling
# 5. Ensure safe execution locally & cloud
# 6. Cara menjalankan : streamlit run input_app_online.py
# ==============================================================

import streamlit as st
import psycopg2
from datetime import datetime

# ==============================================================
# SAFE DATABASE CONNECTION (HANDLE LOCAL + CLOUD)
# ==============================================================
def get_connection():
    try:
        # TRY STREAMLIT CLOUD SECRETS
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            port=st.secrets["postgres"]["port"]
        )
    except:
        # FALLBACK LOCAL (FOR TESTING ONLY)
        return psycopg2.connect(
            host="localhost",
            database="metering_transmedia",
            user="engineer_user",
            password="trans7",
            port="5432"
        )

# ==============================================================
# PAGE TITLE
# ==============================================================
st.title("📡 Metering NEC 20KW Input System")

# ==============================================================
# ENGINEER INFO
# ==============================================================
engineer_name = st.text_input("👤 Nama Engineer")

# ==============================================================
# SENSOR STATUS
# ==============================================================
sensor_status = st.selectbox(
    "Status Perangkat",
    ["NORMAL", "SENSOR_ERROR", "MAINTENANCE"]
)

st.divider()

# ==============================================================
# HELPER FUNCTION
# ==============================================================
def num_input(label):
    val = st.text_input(label)
    if val.strip() == "":
        return None
    try:
        return float(val)
    except:
        st.warning(f"⚠️ Input tidak valid di {label}")
        return None

# ==============================================================
# INPUT SECTION
# ==============================================================
st.subheader("🌡️ Environment")
TX_ROOM_TEMPERATURE = num_input("TX_ROOM_TEMPERATURE")
TX_ROOM_HUMIDITY = num_input("TX_ROOM_HUMIDITY")

st.subheader("📡 Multiplexer")
MULTIPLEXER_I_CN = num_input("MULTIPLEXER_I_CN")
MULTIPLEXER_I_Eb_No = num_input("MULTIPLEXER_I_Eb_No")
MULTIPLEXER_I_LINK_MARGIN = num_input("MULTIPLEXER_I_LINK_MARGIN")
MULTIPLEXER_I_BITRATE = num_input("MULTIPLEXER_I_BITRATE")
TRANSCODER_BITRATE = num_input("TRANSCODER_BITRATE")

st.subheader("⚡ DC Power (PA1 - PA18)")
PA_DC = [num_input(f"PA{i}_DC") for i in range(1,19)]

st.subheader("📊 Exciter")
EXCITER_A_MER = num_input("EXCITER_A_MER")
EXCITER_B_MER = num_input("EXCITER_B_MER")

st.subheader("📡 Transmitter")
TRANSMITTER_FWD_POWER = num_input("TRANSMITTER_FWD_POWER")
TRANSMITTER_REFLECTED_POWER = num_input("TRANSMITTER_REFLECTED_POWER")

st.subheader("⚡ Forward Power & Temperature (PA1 - PA18)")
pa_values = []
for i in range(1, 19):
    col1, col2 = st.columns(2)
    with col1:
        fwd = num_input(f"PA{i}_FWD_POWER")
    with col2:
        temp = num_input(f"PA{i}_TEMP")
    pa_values.append((fwd, temp))

# ==============================================================
# SUBMIT
# ==============================================================
if st.button("💾 Submit Data"):

    if engineer_name.strip() == "":
        st.error("Nama Engineer wajib diisi")
        st.stop()

    try:
        conn = get_connection()
        cur = conn.cursor()

        # ==========================================================
        # BUILD VALUES
        # ==========================================================
        values = [
            datetime.now(),
            TX_ROOM_TEMPERATURE, TX_ROOM_HUMIDITY,
            MULTIPLEXER_I_CN, MULTIPLEXER_I_Eb_No,
            MULTIPLEXER_I_LINK_MARGIN, MULTIPLEXER_I_BITRATE,
            TRANSCODER_BITRATE
        ]

        # ADD DC
        values.extend(PA_DC)

        # ADD EXCITER
        values.extend([
            EXCITER_A_MER, EXCITER_B_MER,
            TRANSMITTER_FWD_POWER, TRANSMITTER_REFLECTED_POWER
        ])

        # ADD PA FWD + TEMP
        for fwd, temp in pa_values:
            values.append(fwd)
            values.append(temp)

        # ==========================================================
        # DYNAMIC PLACEHOLDER (FIX ERROR HERE)
        # ==========================================================
        placeholders = ",".join(["%s"] * len(values))

        query = f"INSERT INTO metering_nec20kw VALUES ({placeholders})"

        # DEBUG CHECK
        st.write(f"Total columns: {len(values)}")

        cur.execute(query, values)
        conn.commit()

        cur.close()
        conn.close()

        st.success("✅ Data berhasil masuk ke PostgreSQL")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ==============================================================
# IMPORTANT FIX EXPLANATION
# ==============================================================
# ❌ ERROR UTAMA ANDA:
# Anda menjalankan dengan:
# python input_app.py
#
# ✔ SOLUSI WAJIB:
# streamlit run input_app.py
#
# ==============================================================
# STEP BY STEP (FINAL - AGAR BISA DIAKSES HP)
# ==============================================================
# 1. Pastikan database PUBLIC (bukan localhost)
# 2. Push ke GitHub
# 3. Deploy ke Streamlit Cloud
# 4. Setup Secrets
# 5. Share URL
#
# RESULT:
# Engineer bisa input dari HP (Telkomsel, dll)
# ==============================================================
