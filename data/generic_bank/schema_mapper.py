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


def generate_sql_create_command(df, column_mapping, primary_key, foreign_keys):
    """
    Generate SQL CREATE TABLE command with primary and foreign key constraints.
    
    :param df: Pandas DataFrame representing the table structure.
    :param column_mapping: Dictionary mapping DataFrame columns to database column names.
    :param primary_key: The column name of the primary key.
    :param foreign_keys: List of dictionaries representing foreign key constraints.
    :return: SQL CREATE TABLE command as a string.
    """
    # Start the SQL command
    sql_command = "CREATE TABLE client (\n"
    
    # Add columns with types inferred from the DataFrame
    for column, mapped_column in column_mapping.items():
        pandas_type = df[column].dtype
        sql_type = pandas_type_to_sql_type(pandas_type)  # Assumes pandas_type_to_sql_type function is defined
        sql_command += f"    {mapped_column} {sql_type},\n"
    
    # Add primary key constraint
    if primary_key:
        sql_command += f"    PRIMARY KEY ({primary_key}),\n"
    
    # Add foreign key constraints
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

    column_mapping = {
        "df_column1": "ID",
        "df_column2": "Name",
        # Add more mappings as necessary
    }






    # Example primary key and foreign keys
    primary_key = "ID"
    foreign_keys = [
        {"column": "ForeignKeyColumn1", "references_table": "OtherTable1", "references_column": "ID"},
        {"column": "ForeignKeyColumn2", "references_table": "OtherTable2", "references_column": "ID"},
        # Add more foreign key constraints as necessary
    ]

    sql_command = generate_sql_create_command(df, column_mapping, primary_key, foreign_keys)
    print(sql_command)

    # client_mapping
    # sm.generate_sql_create_command(df)

    print(df.head())
    print('tested...')
