from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    "postgresql://postgres:123456@localhost:5432/metering2026"
)

df = pd.read_sql("SELECT * FROM metering_nec20kw", engine)