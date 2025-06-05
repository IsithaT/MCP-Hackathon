import psycopg2
from psycopg2.extras import Json

def get_connection():
    return psycopg2.connect(
        dbname="schemaTest.sql",
        user="James",
        password="js205112*",
        host="localhost",
        port="5432"
    )