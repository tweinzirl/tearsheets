import numpy as np
import pandas as pd
from schema_config import data_dict
import warnings


#try:
#    from dbio import connectors
#except ImportError: print("No module named 'dbio', so can't use write_db()")

db = './generic_bank.db'
cobj = None #connectors.SQLite(database=db)

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
    column_mapping, primary_key, foreign_keys = None, None, None
    table_config = schema_config.get(table_name, None)
    if table_config is not None:
        column_mapping = table_config.get('column_mapping', None)
        primary_key = table_config.get('primary_key', None)
        foreign_keys = table_config.get('foreign_keys', None)

    # Start the SQL command
    sql_command = f"CREATE TABLE {table_name} (\n"

    # Add columns with types inferred from the DataFrame
    for column in df.columns:
        pandas_type = df[column].dtype
        sql_type = pandas_type_to_sql_type(pandas_type)
        mapped_column = column
        if isinstance(column_mapping, dict):
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


def generate_schema(cobj, schema_config, save=True):
    """
    Reads a table from a SQLite database and generates an SQL CREATE TABLE command
    based on the DataFrame structure and a given schema configuration.

    :param db_path: Path to the SQLite database.
    :param table_name: Name of the table to read and generate the schema for.
    :param schema_config: Configuration details for schema mapping.
    :return: A string containing the SQL CREATE TABLE command.
    """
    schema = ""
    tables = cobj.read(f"SELECT name FROM sqlite_master WHERE type='table';")
    if tables.empty:
        raise Exception("There are no tables available in the database")

    for table_name in tables.name.to_list():
        df = cobj.read(f"SELECT * FROM {table_name} LIMIT 1;")
        schema += generate_sql_create_command(df, table_name, schema_config=schema_config)
        schema += "\n\n"

    if save:
        with open("Template_SQLite.txt", "w+") as f:
            f.write(schema)

    return schema


def mapper(df, table_name, schema_config):
    """
    Take a dataframe and map the column names and types according to the guidlines in schema_config
    :param df: Pandas dataframe
    :param table_name: Name of the table that corresponds to the dataframe
    :schema_config: Configuration details for schema mapping.
    """
    table_config = schema_config.get(table_name, None)
    if not table_config:
        warnings.warn(f"{table_name} schema config not found. returning original data frame...")
        return df

    column_mapping = table_config.get('column_mapping', None)
    if isinstance(column_mapping, dict):
        try:
            df = df.rename(columns=column_mapping)
            select_columns = [v for _, v in column_mapping.items()]
            df = df[select_columns]
        except Exception as e:
            print(e)
    return df


if __name__ == "__main__":

    import schema_mapper as sm
    sql = generate_schema(cobj, data_dict, save=True)
    print(sql)
