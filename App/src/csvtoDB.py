import pandas as pd
from sqlalchemy import create_engine

# CSV file path
csv_file = '../database/data.csv'
# SQLite database file path
db_file = '../database/database.sqlite3'

# Table name in the SQLite database
table_name = 'order'

# Load the CSV data into a Pandas DataFrame
df = pd.read_csv(csv_file)

# Create the database connection URL
db_url = f'sqlite:///{db_file}'

# Create an SQLAlchemy engine
engine = create_engine(db_url)

# Write the DataFrame to the SQLite database table
df.to_sql(table_name, engine, index=False, if_exists='replace')

# Close the database connection
engine.dispose()
