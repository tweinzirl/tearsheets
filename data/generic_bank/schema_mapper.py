import numpy as np
import pandas as pd
from schema_config import config

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


def generate_sql_create_command(df, table_name, schema_config):
    """
    Generate SQL CREATE TABLE command with primary and foreign key constraints.
    
    :param df: Pandas DataFrame representing the table structure.
    :param table_name: Table name in the database
    :param schema_config: 
        Dictionary contains table name, column_mapping, primary key, and foreign_keys
        column_mapping: Dictionary mapping DataFrame columns to database column names.
        primary_key: The column name of the primary key.
        foreign_keys: List of dictionaries representing foreign key constraints.
    :return: SQL CREATE TABLE command as a string.
    """

    column_mapping = schema_config[table_name].get('column_mapping', None)
    primary_key = schema_config[table_name].get('primary_key', None)
    foreign_keys = schema_config[table_name].get('foreign_keys', None)

    # Start the SQL command
    sql_command = "CREATE TABLE client (\n"
    
    # Add columns with types inferred from the DataFrame
    for column in df.columns:
        pandas_type = df[column].dtype
        sql_type = pandas_type_to_sql_type(pandas_type)
        mapped_column = column
        if isinstance(column_mapping, 'dict'):
            mapped_column = column_mapping.get(column, column)
            
        sql_command += f"    {mapped_column} {sql_type},\n"
    
    # Add primary key constraint
    if primary_key:
        sql_command += f"    PRIMARY KEY ({primary_key}),\n"
    
    # Add foreign key constraints
    if isinstance(foreign_keys, list):
        for fk in foreign_keys:
            sql_command += f"    FOREIGN KEY ({fk['column']}) REFERENCES {fk['references_table']}({fk['references_column']}),\n"
    
    # Remove the last comma and newline
    sql_command = sql_command.rstrip(',\n')
    
    # Finish the SQL command
    sql_command += "\n);"
    
    return sql_command



if __name__ == "__main__":

    import schema_mapper as sm
    db = './generic_bank.db'
    cobj = connectors.SQLite(database=db)
    table_name = "clients"
    schema_config = {table_name : "clients"}
    df =cobj.read(f"select * from {table_name}")

    # client_mapping
    # sm.generate_sql_create_command(df)

    print(df.head())
    print('tested...')
