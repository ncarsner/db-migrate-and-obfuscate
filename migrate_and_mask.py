import pyodbc
import configparser
from datetime import datetime, timedelta
import random
from faker import Faker

# Load configuration settings
config = configparser.ConfigParser()
config.read("config.ini")

# Set source and destination database configurations
source_config = config["db_source"]
target_config = config["db_destination"]

# Declare table variables
table_schema = "dbo"
table_name = "MyTable"
full_table_name = f"[{table_schema}].[{table_name}]"

faker = Faker()

# Identify columns to be obfuscated from source
column_mappings = {
    """Fake or masked data can be generated from SQL statements, Faker providers, lambda functions, or None if NULLs are required
    'ParentReference': 'SELECT Id FROM [dbo].[myParentTable]',
    'FakerField': lambda: faker.name(),
    'IgnoreField': None,
    'RandomInt': lambda: random.randint(0, 3), # parameters from Parent tables or known ranges
    'RandomFloat': lambda: random.uniform(-(10**8), 10**8),
    'RandomDateTime': lambda: datetime(2024, 1, 1) + timedelta(seconds=random.randint(0, 31536000), microseconds=random.randint(0, 999999)),
    """
    "FirstName": lambda: faker.first_name(),
    "MiddleName": lambda: faker.first_name(),
    "LastName": lambda: faker.last_name(),
    "Suffix": lambda: random.choice(["Jr", "Sr", "III","IV",] + [None] * 10),  # overweighted None
    "Email": lambda: faker.safe_email(),
    "WorkPhone": lambda: faker.phone_number(),
    "HireDate": lambda: datetime.combine((datetime.now() - timedelta(days=random.randint(1, 3650))).date(), datetime.min.time()),
}


def connect_to_database(config):
    try:
        conn = pyodbc.connect(
            f'DRIVER={config["driver"]};'
            f'SERVER={config["server"]};'
            f'DATABASE={config["database"]};'
            f'UID={config["user"]};'
            f'PWD={config["pass"]}'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def fetch_data_and_columns(connection, source_table):
    try:
        cursor = connection.cursor()
        # Get column info with no-result query
        cursor.execute(f"SELECT * FROM {source_table} WHERE 1=0;")
        # Wrap column names in brackets
        columns = [column[0] for column in cursor.description]
        # print(f"Fetched columns: {columns}") # DEBUG
        # Fetch data
        cursor.execute(f"SELECT * FROM {source_table};")
        data = cursor.fetchall()
        return data, columns
    except Exception as e:
        print(f"Error fetching data and columns: {e}")
        return [], []


def convert_data(data, columns):
    converted_data = []
    for row in data:
        new_row = []
        for col, item in zip(columns, row):
            if col in column_mappings:
                new_value = column_mappings[col]()
                # print(f"Obfuscating column: {col} with value: {new_value}") # DEBUG
                new_row.append(new_value)
            else:
                if item is None:
                    new_row.append(None)
                elif isinstance(item, bool):
                    new_row.append(1 if item else 0)
                else:
                    new_row.append(item)
        converted_data.append(tuple(new_row))
    return converted_data


"""
Separate IDENTITY INSERT and FOREIGN KEY CONTRAINT scripts, currently included in the insert_data function.

# def enable_identity_insert(cursor, table):
#     print(f"Enabling IDENTITY_INSERT for {table}")
#     cursor.execute(f"SET IDENTITY_INSERT {table} ON")
#     cursor.commit()

# def disable_identity_insert(cursor, table):
#     print(f"Disabling IDENTITY_INSERT for {table}")
#     cursor.execute(f"SET IDENTITY_INSERT {table} OFF")
#     cursor.commit()

# def disable_foreign_key_constraints(cursor):
#     print("Disabling foreign key constraints")
#     cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'")
#     cursor.commit()

# def enable_foreign_key_constraints(cursor):
#     print("Enabling foreign key constraints")
#     cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all'")
#     cursor.commit()
"""


def insert_data(connection, data, columns, target_table):
    """Dynamically construct insert statement and insert data into the target table, handling IDENTITY_INSERT as needed."""
    try:
        cursor = connection.cursor()

        # Check if the table has an identity column
        cursor.execute(
            f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{table_schema}' AND TABLE_NAME = '{target_table}' AND
            COLUMNPROPERTY(object_id(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 1;
        """
        )
        # Determine if IDENTITY_INSERT needs to be turned ON
        identity_column = cursor.fetchone()
        identity_insert = identity_column is not None

        if identity_insert:
            print(f"Enabling IDENTITY_INSERT ON for {target_table}")
            cursor.execute(f"SET IDENTITY_INSERT {target_table} ON;")

        # Disable foreign key constraints
        cursor.execute(f"EXEC sp_msforeachtable @command1='ALTER TABLE {target_table} NOCHECK CONSTRAINT all'")

        columns_list = ", ".join([f"{col}" for col in columns])
        placeholders = ", ".join(["?" for _ in columns])
        insert_query = f"INSERT INTO {target_table} ({columns_list}) VALUES ({placeholders});"

        print(f"SQL Command: {insert_query}")  # DEBUG
        print(f"Number of columns: {len(columns)}")  # DEBUG

        for row in data:
            if len(row) != len(columns):
                raise ValueError("The number of data elements does not match the number of columns.")
            print(f"Inserting row: {row}")
            cursor.execute(insert_query, row)

        connection.commit()

        # Re-enable foreign key constraints
        cursor.execute(f"EXEC sp_msforeachtable @command1='ALTER TABLE {target_table} WITH CHECK CHECK CONSTRAINT all'")

        if identity_insert:
            print(f"Disabling IDENTITY_INSERT for {target_table}")
            cursor.execute(f"SET IDENTITY_INSERT {target_table} OFF")
            # cursor.commit()

    except Exception as e:
        connection.rollback()
        print(f"Error inserting data: {e}")
        print(f"Failed query: {insert_query}")
        print(f"With parameters: {row}")


def main():
    source_conn = connect_to_database(source_config)
    target_conn = connect_to_database(target_config)

    if source_conn and target_conn:
        data, columns = fetch_data_and_columns(source_conn, source_table=table_name)
        if data:
            converted_data = convert_data(data, columns)
            # print(f"Converted data (first 5 rows): {converted_data[:5]}") # DEBUG
            insert_data(target_conn, converted_data, columns, target_table=table_name)
            print("Data migration completed successfully.")
        else:
            print("No data found to migrate.")

        source_conn.close()
        target_conn.close()
    else:
        print("Failed to connect to databases.")


if __name__ == "__main__":
    main()
