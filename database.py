import sqlite3

def delete_existing_db():
    conn = sqlite3.connect('celebrity_airplane.db')  # Creates or connects to a database
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS Airplane')
    cursor.execute('DROP TABLE IF EXISTS Celebrity')
    cursor.execute('DROP TABLE IF EXISTS Planenames')
    cursor.execute('DROP TABLE IF EXISTS Flights')
    conn.commit()
    conn.close()

def create_db():
    conn = sqlite3.connect('celebrity_airplane.db')  # Creates or connects to a database
    cursor = conn.cursor()

    # airplanes table
    # id, tail number, model number

    #Create Airplane Table
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS Planenames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planename TEXT NOT NULL UNIQUE
            )
        '''
    )

    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS Airplane (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planename_id INTEGER NOT NULL,
                tail_number TEXT NOT NULL UNIQUE,
                FOREIGN KEY (planename_id) REFERENCES Planenames (id)
            )
        '''
    )

    # celebrity table
    # id, name, plane id

    #Create Celebrity Table
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS Celebrity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                plane_id INTEGER,
                FOREIGN KEY (plane_id) REFERENCES Airplane (id)
            )
        '''
    )

    # create flights db
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS Flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                distance INTEGER NOT NULL,
                celeb_id INTEGER,
                FOREIGN KEY (celeb_id) REFERENCES Celebrity (id)
            )
        '''
    )

    conn.commit()
    conn.close()


def init_db():
    delete_existing_db()
    create_db()
