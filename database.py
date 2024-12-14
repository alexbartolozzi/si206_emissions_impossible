import sqlite3

conn = sqlite3.connect('celebrity_airplane.db')  # Creates or connects to a database
cursor = conn.cursor()

# airplanes table
# id, tail number, model number

#Create Airplane Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Airplane (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    celebname TEXT NOT NULL,
    planename TEXT NOT NULL,
    tail_number TEXT NOT NULL
)
''')


# celebrity table
# id, name, plane id

#Create Celebrity Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Celebrity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    plane_id INTEGER,
    FOREIGN KEY (plane_id) REFERENCES Airplane (id)
)
''')
conn.commit()
conn.close()

