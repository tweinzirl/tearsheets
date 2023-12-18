Mock data defined in this directory for SQLite database:
 - clients.csv
 - accounts.csv
 - transactions.csv

More sophisticated MySQL (Mariadb) database dumped to fakebank-data-dump-20231206.sql. Steps to load data into 'fakebank' database:
 - Create database within database shell for local user:
   - `MariaDB> create or replace DATABASE fakebank;`
   - `MariaDB> GRANT ALL PRIVILEGES ON fakebank.* TO 'timw'@'localhost';`
   - `MariaDB> FLUSH PRIVILEGES;`
 - Update the collation to be compatible with MariaDB: Change occurrences of `utf8mb4_0900_ai_ci` to `utf8mb4_unicode_520_ci` ([reference](https://dba.stackexchange.com/questions/248904/mysql-to-mariadb-unknown-collation-utf8mb4-0900-ai-ci/298478#298478))
 - Load sql file into database from bash shell:
   - `mariadb -u timw -p fakebank < fakebank-data-dump-20231206.sql`
 - Adding client recommendations (extra data not included in the original data dump) to the database as a table called `recommendations`:
   - load recommendations.csv in memory: `df = pd.read_csv('recommendations.csv')`
   - connect to database with dbio (package available on request): `cobj = dbio.connectors.MySQL(db_user_name, db_password, port=None, database='fakebank')`
   - upload to table: `cobj.write(df, 'recommendations', if_exists='replace')`
