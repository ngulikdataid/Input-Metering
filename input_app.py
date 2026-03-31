# ==============================================================
# STREAMLIT INPUT APP - FULL PARAMETER NEC 20KW
# ==============================================================
# Author  : Data Engineer Mode
# Purpose : Input ALL columns EXACTLY as PostgreSQL table structure
# Notes   :
# - NO column missing
# - Support NULL (sensor error)
# - Preserve data integrity for ML
# ==============================================================

import streamlit as st
import psycopg2
from datetime import datetime

# ==============================================================
# DATABASE CONNECTION FUNCTION
# ==============================================================
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="metering_transmedia",
        user="engineer_user",
        password="123"
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
# HELPER FUNCTION (ALLOW NULL INPUT)
# ==============================================================
def num_input(label):
    val = st.text_input(label)
    if val == "":
        return None
    try:
        return float(val)
    except:
        st.warning(f"⚠️ Input tidak valid di {label}")
        return None

# ==============================================================
# INPUT ALL PARAMETERS (STRICT ORDER)
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
PA1_DC = num_input("PA1_DC")
PA2_DC = num_input("PA2_DC")
PA3_DC = num_input("PA3_DC")
PA4_DC = num_input("PA4_DC")
PA5_DC = num_input("PA5_DC")
PA6_DC = num_input("PA6_DC")
PA7_DC = num_input("PA7_DC")
PA8_DC = num_input("PA8_DC")
PA9_DC = num_input("PA9_DC")
PA10_DC = num_input("PA10_DC")
PA11_DC = num_input("PA11_DC")
PA12_DC = num_input("PA12_DC")
PA13_DC = num_input("PA13_DC")
PA14_DC = num_input("PA14_DC")
PA15_DC = num_input("PA15_DC")
PA16_DC = num_input("PA16_DC")
PA17_DC = num_input("PA17_DC")
PA18_DC = num_input("PA18_DC")

st.subheader("📊 Exciter")
EXCITER_A_MER = num_input("EXCITER_A_MER")
EXCITER_B_MER = num_input("EXCITER_B_MER")

st.subheader("📡 Transmitter")
TRANSMITTER_FWD_POWER = num_input("TRANSMITTER_FWD_POWER")
TRANSMITTER_REFLECTED_POWER = num_input("TRANSMITTER_REFLECTED_POWER")

st.subheader("⚡ Forward Power & Temperature (PA1 - PA18)")

# Generate PA inputs dynamically
pa_values = []
for i in range(1, 19):
    col1, col2 = st.columns(2)
    with col1:
        fwd = num_input(f"PA{i}_FWD_POWER")
    with col2:
        temp = num_input(f"PA{i}_TEMP")
    pa_values.append((fwd, temp))

# ==============================================================
# SUBMIT BUTTON
# ==============================================================
if st.button("💾 Submit Data"):

    if engineer_name == "":
        st.error("Nama Engineer wajib diisi")
        st.stop()

    try:
        conn = get_connection()
        cur = conn.cursor()

        # ==========================================================
        # SQL INSERT QUERY (ALL COLUMNS - STRICT ORDER)
        # ==========================================================
        query = """
        INSERT INTO metering_nec20kw VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s
        )
        """

        # ==========================================================
        # BUILD VALUES
        # ==========================================================
        values = [
            datetime.now(),
            TX_ROOM_TEMPERATURE, TX_ROOM_HUMIDITY,
            MULTIPLEXER_I_CN, MULTIPLEXER_I_Eb_No,
            MULTIPLEXER_I_LINK_MARGIN, MULTIPLEXER_I_BITRATE,
            TRANSCODER_BITRATE,
            PA1_DC, PA2_DC, PA3_DC, PA4_DC, PA5_DC, PA6_DC,
            PA7_DC, PA8_DC, PA9_DC, PA10_DC,
            PA11_DC, PA12_DC, PA13_DC, PA14_DC, PA15_DC,
            PA16_DC, PA17_DC, PA18_DC,
            EXCITER_A_MER, EXCITER_B_MER,
            TRANSMITTER_FWD_POWER, TRANSMITTER_REFLECTED_POWER
        ]

        # append PA values
        for fwd, temp in pa_values:
            values.append(fwd)
            values.append(temp)

        cur.execute(query, values)
        conn.commit()

        cur.close()
        conn.close()

        st.success("✅ Data berhasil masuk ke PostgreSQL")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ==============================================================
# SETUP DATABASE (RUN ONCE IN POSTGRES)
# ==============================================================
# CREATE ROLE engineer_user LOGIN PASSWORD 'trans7';
# GRANT INSERT ON metering_nec20kw TO engineer_user;
# GRANT SELECT ON metering_nec20kw TO engineer_user;

# ==============================================================
# HOW TO RUN
# ==============================================================
# 1. pip install streamlit psycopg2
# 2. streamlit run input_app.py
# ==============================================================
