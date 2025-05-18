import sqlite3

conn = sqlite3.connect('smarthome.db')

c = conn.cursor()

c.execute('DROP TABLE IF EXISTS users')

# Create users table in smarthome database
c.execute( '''
    CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          tag TEXT NOT NULL,
          first_name TEXT NOT NULL,
          last_name TEXT NOT NULL,
          email TEXT NOT NULL,
          profile_picture TEXT NOT NULL,
          light_intensity DECIMAL(10, 2),
          temperature DECIMAL(10, 2),
          humidity DECIMAL(10, 2),
          theme TEXT NOT NULL
          )
          
''')

# Insert user information
# (NOTE: Sofya's RFID value is unknown)
users = [
    (1, "53e9aba5", "Raeeba", "Rahman", "raeeba@gmail.com","../static/Pictures/users/raee-pfp.jpg", 10.0, 22.0, 38, "light-mode"),
    (2, "idk", "Sofya", "Kovalenko", "sofyakovalenko@gmail.com","../static/Pictures/users/sofya-pfp.jpg", 275.0, 20.0, 45, "dark-mode"),
    (3, "3dd64f7", "Ike", "Obodoechina", "ike@gmail.com","../static/Pictures/users/ike-pfp.jpg", 500.0, 24.0, 10, "dark-mode")
]

c.executemany( '''
INSERT INTO users (id, tag, first_name, last_name, email, profile_picture, light_intensity, temperature, humidity, theme)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          
''', users)

c.execute('SELECT * FROM users')
rows = c.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()

# IMPORTANT: Run file whenever user info is modified to update the database 
print("Table created successfully.")