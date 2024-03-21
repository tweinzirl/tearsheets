import numpy as np
import pandas as pd

try:
    from dbio import connectors
except ImportError: print("No module named 'dbio', so can't use write_db()")


def pandas_type_to_sql_type(pandas_type):
    """
    Convert pandas data type to SQL data type.
    """
    if pd.api.types.is_integer_dtype(pandas_type):
        return "integer"
    elif pd.api.types.is_float_dtype(pandas_type):
        return "real"
    elif pd.api.types.is_datetime64_any_dtype(pandas_type):
        return "date"
    elif pd.api.types.is_string_dtype(pandas_type):
        return "varchar(128)"
    elif pd.api.types.is_bool_dtype(pandas_type):
        return "boolean"
    else:
        return "varchar(128)"  # Default fallback


def generate_sql_create_command(df, column_mapping):
    """
    Generate SQL CREATE TABLE command based on DataFrame columns and inferred data types.
    
    :param df: Pandas DataFrame to be used for generating SQL command.
    :param column_mapping: Dictionary mapping DataFrame columns to pre-defined columns.
    :return: String containing SQL CREATE TABLE command.
    """
    # Rename DataFrame columns based on mapping
    df = df.rename(columns=column_mapping)
    
    # Start the SQL command
    sql_command = "CREATE TABLE client (\n"
    
    # Iterate over DataFrame columns to generate SQL column definitions
    for column in df.columns:
        pandas_type = df[column].dtype
        sql_type = pandas_type_to_sql_type(pandas_type)
        sql_command += f"    {column} {sql_type},\n"
    
    # Remove the last comma and newline
    sql_command = sql_command.rstrip(',\n')
    
    # Finish the SQL command
    sql_command += "\n);"
    
    return sql_command


if __name__ == "__main__":
    import schema_mapper as sm
    db = './generic_bank.db'
    cobj = connectors.SQLite(database=db)
    df =cobj.read("select * from clients")




    print(df.head())
    print('tested...')
