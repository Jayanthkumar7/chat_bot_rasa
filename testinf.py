import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/bookticket.db')
cursor = conn.cursor()

# Execute the query
cursor.execute("""SELECT ename FROM events""")

# Fetch all results
events = cursor.fetchall()

# Print each event name
li=[]
for event in events:
    li.append(event[0])
print(li)

conn.close()
