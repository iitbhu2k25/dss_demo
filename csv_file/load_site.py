import pandas as pd
from sqlalchemy import create_engine

# Database connection details
DB_USER = 'myuser'
DB_PASSWORD = 'mypassword'
DB_HOST = 'localhost'
DB_PORT = '5431'
DB_NAME = 'mydatabase'

# Table name and CSV file
TABLE_NAME = 'stp_data'
CSV_FILE = 'load2.csv'

# Create the database engine
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def load_csv_to_db():
    try:
        # Read the CSV file
        df = pd.read_csv(CSV_FILE)
        
        # Store data in the database
        df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
        print(f"Data from {CSV_FILE} has been successfully inserted into {TABLE_NAME}.")
    
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    load_csv_to_db()
