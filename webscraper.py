from bs4 import BeautifulSoup
import sqlite3
import requests

def get_celebrity_airplanes():
    url = "https://celebrityprivatejettracker.com/#gref"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    parentspan = soup.findAll('span', class_="tooltipa")

    celeb_list = []
    unwanted_entries = {"PST", "EST", "CST", "MST", "", "Bahamas"}  # Skip unwanted names

    for each in parentspan:
        name_tag = each.find('a', class_="maincolor")
        if not name_tag:
            continue
        
        name = name_tag.text.strip()
        # Skip unwanted entries
        if name in unwanted_entries:
            continue

        # Extract plane name
        plane_info = name_tag.find_next(string=True)
        plane_name = plane_info.find_next(string=True).strip() if plane_info else None
        if plane_name and '(' in plane_name:
            plane_name = plane_name.split('(')[0].strip()

        # Extract tail number
        tailnumber_tag = name_tag.find_next("a", href=True)
        tail_number = tailnumber_tag.text.strip() if tailnumber_tag else None

        celeb_list.append({
            "name": name,
            "plane": plane_name,
            "tailnumber": tail_number
        })
    return celeb_list

def insert_data(celeb_list):
    conn = sqlite3.connect('celebrity_airplane.db')
    cursor = conn.cursor()

    # Clear old data if you want a fresh start each run
    cursor.execute('DELETE FROM Celebrity')
    cursor.execute('DELETE FROM Planenames')
    cursor.execute('DELETE FROM Airplane')
    conn.commit()

    for celeb in celeb_list:
        name = celeb['name']
        plane_name = celeb['plane']
        tail_number = celeb['tailnumber']

        # Insert or get the Celebrity ID
        cursor.execute('SELECT id FROM Celebrity WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            celeb_id = row[0]
        else:
            cursor.execute('INSERT INTO Celebrity (name) VALUES (?)', (name,))
            celeb_id = cursor.lastrowid

        # Insert or get the Planename ID (if plane_name is not None)
        if plane_name:
            cursor.execute('SELECT id FROM Planenames WHERE planename = ?', (plane_name,))
            row = cursor.fetchone()
            if row:
                planename_id = row[0]
            else:
                cursor.execute('INSERT INTO Planenames (planename) VALUES (?)', (plane_name,))
                planename_id = cursor.lastrowid
        else:
            # If no plane name, skip inserting airplane
            continue

        # Insert the Airplane if the tail_number is unique
        if tail_number:
            cursor.execute('SELECT id FROM Airplane WHERE tail_number = ?', (tail_number,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO Airplane (celeb_id, planename_id, tail_number)
                    VALUES (?, ?, ?)
                ''', (celeb_id, planename_id, tail_number))
                
                # If desired, update Celebrity's plane_id to reference this Airplane
                # airplane_id = cursor.lastrowid
                # cursor.execute('UPDATE Celebrity SET plane_id = ? WHERE id = ?', (airplane_id, celeb_id))

    conn.commit()
    conn.close()

def finish_web_scrape():
    celeb_list = get_celebrity_airplanes()
    insert_data(celeb_list)
    print("Web scrape finished")

finish_web_scrape()