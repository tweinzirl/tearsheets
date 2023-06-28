import os
import glob
import pandas as pd
import dbio  # local pkg


if __name__ == '__main__':

    # db connection
    cobj = dbio.connectors.SQLite('fake_bank.db')

    # table discovery
    tables = glob.glob('*csv')

    # read and write table
    for csv in tables:
        table = csv.split('.csv')[0]
        df = pd.read_csv(csv, comment='#')
        print(csv)
        print(df.head(1))

        cobj.write(df, table, if_exists='replace')

    # check db contents
    master = cobj.read('select * from sqlite_master')
    print(master)
