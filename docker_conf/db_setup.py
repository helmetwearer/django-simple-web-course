import psycopg2
import os
from psycopg2.extensions import AsIs
import time 

print('Pausing 3 seconds to make sure POSTGRES has launched')
time.sleep(3)

connection = None
CONNECT_STRING = "user='{}' host='{}' password='{}' port='{}'".format(
    os.environ["POSTGRES_USER"],
    os.environ["POSTGRES_HOST"],
    os.environ["POSTGRES_PASSWORD"],
    os.environ["POSTGRES_PORT"],
)
try:
    # In PostgreSQL, default username is 'postgres' and password is 'postgres'.
    # And also there is a default database exist named as 'postgres'.
    # Default host is 'localhost' or '127.0.0.1'
    # And default port is '5432'.
    connection = psycopg2.connect(CONNECT_STRING)
    print('Database connected.')

except:
    print('Database not connected.')

if connection is not None:
    connection.autocommit = True
    cur = connection.cursor()

    print("Checking if user {} exists".format(os.environ["DB_USER"]))
    cur.execute('SELECT usename FROM pg_user,pg_roles WHERE oid=usesysid;')
    username_list = cur.fetchall()
    if (os.environ["DB_USER"],) in username_list:
        print("User {} exists".format(os.environ["DB_USER"]))
    else:
        print("User {} does not exist. Creating.".format(
            os.environ["DB_USER"]))
        cur.execute("create user %s with password %s",
                    (AsIs(os.environ["DB_USER"]), os.environ["DB_PASS"],))
        print("User {} created.".format(os.environ["DB_USER"]))

    print("Checking to see if database {} exists".format(
        os.environ["DB_NAME"]))

    cur.execute("SELECT datname FROM pg_database;")

    list_database = cur.fetchall()

    if (os.environ["DB_NAME"],) in list_database:
        print("'{}' Database already exists. Skipping.".format(
            os.environ["DB_NAME"]))
    else:
        print("'{}' Database does not exist. Creating.".format(
            os.environ["DB_NAME"]))
        cur.execute('Create database "{}"'.format(os.environ["DB_NAME"]))

        print('connecting to new database')
        connection2 = psycopg2.connect(
            user=os.environ["POSTGRES_USER"], 
            database=os.environ["DB_NAME"], 
            host=os.environ["POSTGRES_HOST"], 
            password=os.environ["POSTGRES_PASSWORD"], 
            port=os.environ["POSTGRES_PORT"])
        print('connected. Enabling postgis');
        connection2.autocommit=True;
        cur2 = connection2.cursor()
        cur2.execute('CREATE EXTENSION postgis')
        print('postgis extension created')
        cur2.execute('CREATE EXTENSION pg_trgm')
        print('Trigram Index extenion created')
        connection2.close()
        print("'{}' Created. Granting privileges to {}".format(
            os.environ["DB_NAME"], os.environ["DB_USER"]))
        cur.execute('GRANT ALL PRIVILEGES ON DATABASE "{}" TO {};'.format(
            os.environ["DB_NAME"], os.environ["DB_USER"]))
        print("All privileges granted to {} on {}".format(
            os.environ["DB_USER"], os.environ["DB_NAME"]))
        print("Changing ownership to {} on {}".format(
            os.environ["DB_USER"], os.environ["DB_NAME"]))
        cur.execute('ALTER DATABASE "{}" OWNER TO {};'.format(
            os.environ["DB_NAME"], os.environ["DB_USER"]))
        cur.execute('ALTER SCHEMA public OWNER TO {};'.format(
            os.environ["DB_USER"]))
        print("Owner changed")

    connection.close()
    connection = psycopg2.connect(
        user=os.environ["POSTGRES_USER"],
        database=os.environ["DB_NAME"],
        host=os.environ["POSTGRES_HOST"],
        password=os.environ["POSTGRES_PASSWORD"],
        port=os.environ["POSTGRES_PORT"]
    )
    cur = connection.cursor()
    cur.execute('ALTER SCHEMA public OWNER TO {};'.format(os.environ["DB_USER"]))
    print('owner of public schema updated')
    cur.execute('GRANT ALL PRIVILEGES ON SCHEMA public TO {};'.format(os.environ["DB_USER"]))
    print('privileges granted')
    connection.commit()

    connection.close()