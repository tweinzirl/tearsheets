import numpy as np
import pandas as pd

try:
    from dbio import connectors
except ImportError: print("No module named 'dbio', so can't use write_db()")

if __name__ == "__main__":
    import schema_mapper as sm
    db = './generic_bank.db'
    cobj = connectors.SQLite(database=db)
    df =cobj.read("select * from clients")
    print(df.head())
    print('tested...')
