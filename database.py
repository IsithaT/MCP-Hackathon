import psycopg2

conn = psycopg2.connect(
    database = "testdb", 
    user = "postgres", 
    host= 'localhost',
    password = "js205112*",
    port = 5432
)
cur = conn.cursor()
cur.execute('select * from api_configurations')

rows = cur.fetchall()
conn.commit()
conn.close()
for row in rows:
    print(row)