import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,text

load_dotenv()

def get_engine():
    url = (
        f"postgresql+psycopg://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}"
        f"@{os.environ['PGHOST']}:{os.environ['PGPORT']}/{os.environ['PGDATABASE']}"
    )
    return create_engine(url)

if __name__ == "__main__":
    with get_engine().connect() as conn:
        print(conn.execute(text("SELECT current_database(), version()")).one())
