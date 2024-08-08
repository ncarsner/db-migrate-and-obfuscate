# Fake Data Generator

## Overview
This repository contains code for the purposes of generating obfuscated data from an existing CSV file and provides options to export the data to Excel, CSV, or write directly to a SQL Server database. It contains methods for obfuscating data <i>(e.g. migrating Production data to a lower environment for testing)</i>, and allows users to choose their preferred output format interactively. It also contains methods for rendering fake data from user-defined subjects and corresponding data types.

## Key Components

### Variables and Configurations
- `file_source`: Path to the source CSV file containing the original data.
- `file_destination`: Path for the destination Excel file.
- `csv_destination`: Path for the destination obfuscated CSV file.
- `columns_to_obfuscate`: List of column names in the DataFrame that need to be obfuscated.
- `config`: Configuration file containing database connection details.

### Functions and Classes
- `DataObfuscator`: Class with a method `obfuscate_column` to obfuscate specified columns in the DataFrame.
- `export_to_excel`: Function to export original and obfuscated data to an Excel file.
- `export_to_csv`: Function to export obfuscated data to a CSV file.
- `write_to_database`: Function to write obfuscated data to a SQL Server database using config connection details.
- `main`: Main function to load data, apply obfuscation, and prompt user for output method.

## How to use this code
1. Clone the repository: `git clone https://github.com/ncarsner/db-migrate-and-obfuscate.git`
2. Create and activate a virtual environment: `venv`
3. Import requirements file in the terminal: `pip install -r requirements.txt`
4. Set variables as identified in the below section.
5. Execute `faker_from_file.py` script to mask data from an existing file.
6. Execute `faker_to_file.py` script to create fake data from scratch; users to define subjects and data types.
7. Execute `migrate_and_mask.py` script to mask data in-flight from source to destination db. This requires compatible schemas.

### Prerequisites
- Python 3.x
- Required Python libraries:
    * `Faker`
    * `openpyxl`
    * `pandas`
    * `pyodbc`
    * `SQLAlchemy`

###
| File | Purpose |
|:------------- |:-------------|
| `faker_from_file` | obfuscates data from source file, for exporting to CSV or XLSX file, or writing to db |
| `faker_to_file` | standalone Faker generator that exports to CSV, JSON, or XLSX file |
| `migrate_and_mask` | obfuscates defined data from source db and writes to destination db |
|
| `fake_data` | includes arrays of custom lists that can be used with lambda functions |
| `faker_samples_all` | includes rendered examples of most Faker provider types |

## Testing
Test suite for this repository is pending.

## License
There is no license for this repository. This repository is intended for organizational use only.

## Contributing
Contributions are welcome. Please open an issue or submit a pull request for any improvements or bug fixes.

---
