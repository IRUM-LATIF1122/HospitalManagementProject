import oracledb

# Initialize Oracle client in thick mode (use your actual folder)
oracledb.init_oracle_client(lib_dir=r"D:\instantclient_19_28")

def get_connection():
    try:
        conn = oracledb.connect(
            user="scott",
            password="tiger",
            dsn="localhost/orcl"
        )
        print("✅ Database connected successfully!")
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        return None
