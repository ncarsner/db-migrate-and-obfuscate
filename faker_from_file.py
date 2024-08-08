from faker import Faker
import pandas as pd
from openpyxl import load_workbook
from configparser import ConfigParser
import pyodbc
import os

fake = Faker()


class DataObfuscator:
    """A class to obfuscate specific columns in a pandas DataFrame using data from the Faker library.

    Attributes:
        fake_methods (dict): A mapping from keywords in column names to corresponding Faker methods.
    """

    def __init__(self):
        """Initializes the DataObfuscator with predefined mappings of column name parts to Faker methods."""
        self.fake_methods = {
            "name": "name",
            "addr": "street_address",
            "address": "street_address",
            "city": "city",
            "st": "state_abbr",
            "state": "state_abbr",
            "zip": "zipcode",
            "postcode": "zipcode",
        }

    def guess_fake_method(self, column_name):
        """Guesses the appropriate Faker method based on substrings found in the column name.

        Args:
            column_name (str): The name of the column for which to determine the Faker method.
        Returns:
            str: The name of the Faker method that seems most appropriate for the given column name.
        """
        column_name_lower = column_name.lower()
        for key, method in self.fake_methods.items():
            if key in column_name_lower:
                return method

        return "text"  # Default to a generic text if no match is found

    def obfuscate_column(self, df, column_name, columns_to_obfuscate):
        """Obfuscates the specified column if it is in the columns_to_obfuscate list and exists in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the column to be obfuscated.
            column_name (str): The name of the column to obfuscate.
            columns_to_obfuscate (list): A list of column names that are desined to be obfuscated.

        Prints:
            Information about the obfuscation process and any issues encountered.
        """
        # Check if the column is in the allowed list and obfuscate if it is
        if column_name in columns_to_obfuscate and column_name in df.columns:
            fake_method = self.guess_fake_method(column_name)
            obfuscation_function = getattr(fake, fake_method)
            df[column_name] = [obfuscation_function() for _ in range(len(df))]
            print(f"'{column_name}' obfuscated using '{fake_method}' Faker method.")
        else:
            if column_name not in columns_to_obfuscate:
                print(f"Column '{column_name}' not in allowed obfuscation list.")
            if column_name not in df.columns:
                print(f"Column '{column_name}' not found in DataFrame.")


def export_to_excel(df_original, df_obfuscated, file_destination):
    try:
        book = load_workbook(file_destination)
        writer = pd.ExcelWriter(file_destination, engine="openpyxl")
        writer.book = book
    except FileNotFoundError:
        writer = pd.ExcelWriter(file_destination, engine="openpyxl")

    with writer:
        df_original.to_excel(writer, sheet_name="Original", index=False)
        df_obfuscated.to_excel(writer, sheet_name="Obfuscated", index=False)

    print(f"Data saved to {file_destination} with 'Obfuscated' sheet added.")


def export_to_csv(df_obfuscated, file_destination):
    csv_obfuscated = os.path.splitext(file_destination)[0] + "_obfuscated.csv"
    df_obfuscated.to_csv(csv_obfuscated, index=False)
    print(f"Obfuscated data saved to {csv_obfuscated}")


def write_to_database(df_obfuscated, table_name):
    config = ConfigParser()
    config.read("config.ini")

    driver = config["db_destination"]["driver"]
    server = config["db_destination"]["server"]
    database = config["db_destination"]["database"]
    username = config["db_destination"]["user"]
    password = config["db_destination"]["pass"]

    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    try:
        conn = pyodbc.connect(connection_string)

        # Write the obfuscated DataFrame to SQL Server
        df_obfuscated.to_sql(table_name, conn, if_exists="replace", index=False, method="multi")

        conn.commit()
        print(f"Obfuscated data written to table '{table_name}'")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def main():
    # Define the file paths and columns
    file_source = r"C:\Users\MyUser\sourceData.csv"
    file_destination = os.path.splitext(file_source)[0]  # + ".csv"

    columns_to_obfuscate = [
        "FirstName",
        "MiddleName",
        "LastName",
        "Suffix",
        "Email",
        "WorkPhone",
        "Extension",
        "MobilePhone",
        "Fax",
        "SupervisorName",
        "SupervisorEmail",
        "SupervisorPhone",
        "ComplianceOfficer",
        "ComplianceOfficerEmail",
        "ComplianceOfficerPhone",
    ]

    # Load the DataFrame from the source CSV file
    try:
        df_original = pd.read_csv(file_source)
    except FileNotFoundError:
        print(f"Error: The file {file_source} was not found.")
        return

    # Create a copy of the DataFrame for obfuscation
    df_obfuscated = df_original.copy()

    # Initialize the obfuscator and apply to allowed columns
    obfuscator = DataObfuscator()
    for column in df_obfuscated.columns:
        obfuscator.obfuscate_column(df_obfuscated, column, columns_to_obfuscate)

    # Prompt user for preferred output method
    print("Choose output method:")
    print("1. Export to Excel")
    print("2. Export to CSV")
    print("3. Write to Database")
    print("-- PRESS ANY OTHER KEY TO EXIT --\n")
    choice = input("Enter selection: ")

    if choice == "1":
        export_to_excel(df_obfuscated, file_destination)
    elif choice == "2":
        export_to_csv(df_obfuscated, file_destination)
    elif choice == "3":
        table_name = input("Enter the SQL Server table name: ")
        write_to_database(df_original, df_obfuscated, table_name)
    else:
        print("Invalid choice. Exiting the program.")
        exit()


if __name__ == "__main__":
    main()
