import pandas as pd
from pathlib import Path

# ==============================
# CONFIG
# ==============================
csv_path = r"C:\Users\ronny\Documents\Postgresql_Projects\metering_nec_20kw - cleaned.csv"
sql_output_path = r"C:\Users\ronny\Documents\Postgresql_Projects\metering_nec_20kw - cleaned.sql"

table_name = "metering_nec20kw"

# ==============================
# LOAD CSV (PRESERVE ORIGINAL PRECISION)
# ==============================
# IMPORTANT: do NOT force float formatting here
df = pd.read_csv(csv_path, dtype=str)

# ==============================
# CLEAN COLUMN NAMES
# ==============================
df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]

expected_columns = [
    "Timestamp","TX_ROOM_TEMPERATURE","TX_ROOM_HUMIDITY","MULTIPLEXER_I_CN","MULTIPLEXER_I_Eb_No",
    "MULTIPLEXER_I_LINK_MARGIN","MULTIPLEXER_I_BITRATE","TRANSCODER_BITRATE",
    "PA1_DC","PA2_DC","PA3_DC","PA4_DC","PA5_DC","PA6_DC","PA7_DC","PA8_DC","PA9_DC","PA10_DC",
    "PA11_DC","PA12_DC","PA13_DC","PA14_DC","PA15_DC","PA16_DC","PA17_DC","PA18_DC",
    "EXCITER_A_MER","EXCITER_B_MER","TRANSMITTER_FWD_POWER","TRANSMITTER_REFLECTED_POWER",
    "PA1_FWD_POWER","PA1_TEMP","PA2_FWD_POWER","PA2_TEMP","PA3_FWD_POWER","PA3_TEMP",
    "PA4_FWD_POWER","PA4_TEMP","PA5_FWD_POWER","PA5_TEMP","PA6_FWD_POWER","PA6_TEMP",
    "PA7_FWD_POWER","PA7_TEMP","PA8_FWD_POWER","PA8_TEMP","PA9_FWD_POWER","PA9_TEMP",
    "PA10_FWD_POWER","PA10_TEMP","PA11_FWD_POWER","PA11_TEMP","PA12_FWD_POWER","PA12_TEMP",
    "PA13_FWD_POWER","PA13_TEMP","PA14_FWD_POWER","PA14_TEMP","PA15_FWD_POWER","PA15_TEMP",
    "PA16_FWD_POWER","PA16_TEMP","PA17_FWD_POWER","PA17_TEMP","PA18_FWD_POWER","PA18_TEMP"
]

# Reorder strictly
missing = set(expected_columns) - set(df.columns)
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

df = df[expected_columns]

# ==============================
# FIX TIMESTAMP ONLY
# ==============================
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
if df['Timestamp'].isna().any():
    raise ValueError("Invalid Timestamp format detected in CSV")

# ==============================
# SQL TYPE (FLEXIBLE PRECISION)
# ==============================
column_types = {}
for col in df.columns:
    if col == "Timestamp":
        column_types[col] = "TIMESTAMP"
    else:
        column_types[col] = "NUMERIC"

# ==============================
# GENERATE CREATE TABLE
# ==============================
create_stmt = f"CREATE TABLE {table_name} (\n"
for col in df.columns:
    create_stmt += f"    {col} {column_types[col]},\n"
create_stmt = create_stmt.rstrip(",\n") + "\n);\n\n"

# ==============================
# FORMAT VALUE (PRESERVE DECIMAL EXACTLY)
# ==============================
def format_value(val, col):
    if pd.isna(val) or val == "":
        return "NULL"

    if col == "Timestamp":
        return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"

    # IMPORTANT: keep original string (no rounding!)
    return str(val)

# ==============================
# GENERATE INSERT STATEMENTS
# ==============================
insert_statements = ""
for _, row in df.iterrows():
    values = ", ".join([format_value(row[col], col) for col in df.columns])
    insert_statements += f"INSERT INTO {table_name} VALUES ({values});\n"

# ==============================
# WRITE TO FILE
# ==============================
with open(sql_output_path, "w", encoding="utf-8") as f:
    f.write(create_stmt)
    f.write(insert_statements)

# ==============================
# VALIDATION OUTPUT
# ==============================
print("====================================")
print("SQL file successfully generated")
print("Output:", sql_output_path)
print("Total rows (CSV):", len(df))
print("Total INSERT generated:", len(df))
print("DECIMAL PRESERVED EXACTLY (NO ROUNDING)")
print("====================================")
