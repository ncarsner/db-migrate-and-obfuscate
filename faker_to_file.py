import os
import csv
import json
import random
from faker import Faker
from datetime import datetime, timedelta
from openpyxl import Workbook
import time

import fake_data

# Variables for min and max ranges for numeric types
min_bigint = -9223372036854775808
max_bigint = 9223372036854775807

min_int = -2147483648
max_int = 2147483647

min_smallint = -32768
max_smallint = 32767

min_tinyint = 0
max_tinyint = 255

min_float = -(10**18)
max_float = 10**18

min_dollar = -(10**8)
max_dollar = 10**8


def generate_null_or_value(value, null_percentage):
    """
    Generate a null or non-null value based on the specified null_percentage.

    Args:
        value: The value to return if it's not null.
        null_percentage (float): The percentage probability of returning a null value.
            Must be a float between 0 and 1.

    Returns:
        object: Either the provided value or None, depending on the random selection.

    Example:
        # Generate null or non-null value with 20% probability of null
        result = generate_null_or_value("example_value", 0.2)
    """
    return None if random.random() < null_percentage else value


def generate_random_datetime(start_date=None, end_date=None, years=None):
    """
    Generate a random datetime within the specified range.

    Args:
        start_date (datetime, optional): The start of the date range. Defaults to 5 years prior to current date.
        end_date (datetime, optional): The end of the date range. Defaults to 5 years ahead of current date.
        years (int, optional): The number of years to consider if start_date or end_date is not provided.
            Defaults to 5.

    Returns:
        datetime: A random datetime within the specified range.

    Example:
        # Generate a random datetime within the year 2024
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        random_date = generate_random_datetime(start_date, end_date)
    """
    if years is None:
        years = 5
    if start_date is None:
        start_date = datetime.now() - timedelta(days=years * 365)
    if end_date is None:
        end_date = datetime.now() + timedelta(days=years * 365)

    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, delta.seconds)

    return start_date + timedelta(days=random_days, seconds=random_seconds)


def generate_mock_data(data_type, include_nulls, null_percentage=0.1):
    """
    Generate mock data based on the specified data type.

    Args:
        data_type (str or callable): The type of data to generate.
            Supported data types: 'char', 'string', 'text', 'date', 'datetime',
            'bit', 'boolean', 'float', 'numeric', 'money', 'smallint', 'tinyint',
            'bigint', 'int', 'integer', 'age', or a custom function.
        include_nulls (bool): Flag indicating whether to include null values.

    Returns:
        object: Mock data based on the specified data type.

    Example:
        # Generate mock string data with possibility of null values
        mock_string = generate_mock_data('string', include_nulls=True)
    """
    null_percentage = null_percent if include_nulls else 0

    if callable(data_type):
        return data_type()
    elif isinstance(data_type, str) and data_type.lower() in ["char", "string", "text"]:
        return generate_null_or_value(faker.word(), null_percentage)
    elif data_type.lower() == "date":
        return generate_null_or_value(generate_random_datetime(start_date=None, end_date=None, years=None).date(), null_percentage)
    elif data_type.lower() == "datetime":
        return generate_null_or_value(generate_random_datetime(start_date=None, end_date=None, years=None), null_percentage)
    elif data_type.lower() in ["bit", "boolean"]:
        return generate_null_or_value(random.choice([0, 1]), null_percentage)
    elif data_type.lower() == "float":
        return generate_null_or_value(random.uniform(min_float, max_float), null_percentage)
    elif data_type.lower() in ["numeric", "money"]:
        return generate_null_or_value(round(random.uniform(min_dollar, max_dollar), 2), null_percentage)
    elif data_type.lower() == "smallint":
        return generate_null_or_value(random.randint(min_smallint, max_smallint), null_percentage)
    elif data_type.lower() == "tinyint":
        return generate_null_or_value(random.randint(min_tinyint, max_tinyint), null_percentage)
    elif data_type.lower() == "bigint":
        return generate_null_or_value(random.randint(min_bigint, max_bigint), null_percentage)
    elif data_type.lower() in ["int", "integer"]:
        return generate_null_or_value(random.randint(min_int, max_int), null_percentage)
    elif data_type.lower() == "age":
        return generate_null_or_value(random.randint(18, 80), null_percentage)
    else:
        return generate_null_or_value(faker.word(), null_percentage)


def generate_mock_records(columns, num_records, include_nulls):
    """
    Generate mock records based on the specified columns with a percentage of null values.

    Args:
        columns (dict): A dictionary where keys are column names and values are either data types
            (str) or tuples of data types and include_null flags.
        num_records (int): The number of records to generate.
        include_nulls (bool): Flag indicating whether to include null values.

    Returns:
        list: A list of dictionaries representing mock records.

    Example:
        # Generate mock records with specified columns and include null values
        columns = {
            'name': 'string',
            'age': ('age', True),
            'birthdate': ('date', False)
        }
        mock_records = generate_mock_records(columns, num_records=10, include_nulls=True)
    """
    records = []
    for _ in range(num_records):
        record = {}
        for col_name, data_info in columns.items():
            if isinstance(data_info, tuple):
                data_type, include_null = data_info
                record[col_name] = generate_mock_data(data_type, include_nulls and include_null)
            else:
                record[col_name] = data_info(_)
        records.append(record)
    return records


def export_to_csv(records, filename):
    """
    Export records to a CSV file.

    Args:
        records (list of dict): A list of dictionaries representing records.
        filename (str): The filename to save the CSV file.

    Returns:
        None

    Example:
        # Export records to a CSV file named 'data.csv'
        export_to_csv(records, "data.csv")
    """
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=records[0].keys())
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def export_to_json(records, filename):
    """
    Export records to a JSON file.

    Args:
        records (list): A list of records to export.
        filename (str): The filename to save the JSON file.

    Returns:
        None

    Example:
        # Export records to a JSON file named 'data.json'
        export_to_json(records, "data.json")
    """
    with open(filename, "w") as jsonfile:
        json.dump(records, jsonfile, indent=4)


def export_to_excel(records, filename):
    """
    Export records to an Excel file.

    Args:
        records (list of dict): A list of dictionaries representing records.
        filename (str): The filename to save the Excel file.

    Returns:
        None

    Example:
        # Export records to an Excel file named 'data.xlsx'
        export_to_excel(records, "data.xlsx")
    """
    wb = Workbook()
    ws = wb.active
    ws.append(records[0].keys())
    for record in records:
        ws.append(list(record.values()))
    wb.save(filename)


if __name__ == "__main__":
    start_time = time.time()
    # Define column names and data types as -- ColumnName : (lambda or datatype, True/False include nulls)
    columns = {
        "Index": lambda idx: idx + 1,  # autoincrement index PK column
        "FirstName": (lambda: random.choice(fake_data.first_name), True),
        "EmployeeId": ("int", False),
        "HireDate": ("date", True),
        "Active": ("bit", False),
        "IsEmployee": ("boolean", False),
        "LastUpdated": ("datetime", True),
        "Description": ("string", True),
        "Score": ("integer", False),
        "Salary": (lambda: random.uniform(40_000, 120_000), True),
        "Revenue": ("numeric", True),
        "Amount": ("money", True),
        # "Age": ("smallint", False),
        "Date of Birth": ("date", True),
        "Age": (lambda: random.randint(18, 80) if random.random() > null_percent else None, True),
        "Savings": ("bigint", True),
        "Comments": (lambda: random.choice(fake_data.fake_data_lorem), True),

        "Address": (lambda: faker.address(), True),
        "Address 1": (lambda: faker.building_number(), True),
        "Email": (lambda: faker.email(), True),
        "Phone": (lambda: faker.phone_number(), True),
        "Country": (lambda: faker.country(), True),
        "SSN": (lambda: faker.random_number(digits=9), False),
        "MaritalStatus": (lambda: faker.random_element(elements=("Single", "Married", "Divorced", "Widowed", None)), True),
        "JoinDate": ("date", True),
        "Manager": (lambda: faker.name(), True),
        "Department": (lambda: random.choice(fake_data.departments), True),
        "Job Title": (lambda: random.choice(fake_data.job_titles), True),
        "Education": (lambda: faker.random_element(elements=("High School", "Bachelor's", "Master's", "PhD")), True),
        "YearsExperience": ("integer", False),
        "Certifications": (lambda: faker.random_element(elements=("CCNA", "PMP", "CEH", "AWS", None)), True),
        "LicenseNumber": ("string", True),
        "Membership": ("boolean", False),
        "TimeStamp": ("datetime", True),

    }

    num_records = 1_000
    include_nulls = True
    null_percent = 0.20
    output_format = "csv"
    output_directory = r"C:\Users\myUser\Documents"
    
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    faker = Faker()

    # Generate mock data
    mock_records = generate_mock_records(columns, num_records, include_nulls)

    # Create output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Export data based on output format
    if output_format == "csv":
        export_to_csv(mock_records, os.path.join(output_directory, f"mock_data_{current_time}.csv"))
    elif output_format == "json":
        export_to_json(mock_records, os.path.join(output_directory, f"mock_data_{current_time}.json"))
    elif output_format == "xlsx":
        export_to_excel(mock_records, os.path.join(output_directory, f"mock_data_{current_time}.xlsx"))
    else:
        print("Unsupported output format")

    # Calculate execution time
    end_time = time.time()

    execution_time_seconds = end_time - start_time
    minutes = int(execution_time_seconds // 60)
    seconds = int(execution_time_seconds % 60)
    milliseconds = int((execution_time_seconds - int(execution_time_seconds)) * 1000)

    if minutes > 0:
        if seconds > 0:
            print(f"{num_records:,} records produced in: {minutes}:{seconds}.")
        else:
            print(f"{num_records:,} records produced in: {minutes} minutes.")
    else:
        if milliseconds > 0:
            print(f"{num_records:,} records produced in: {seconds}.{milliseconds} seconds.")
        else:
            print(f"{num_records:,} records produced in: {seconds} seconds.")
