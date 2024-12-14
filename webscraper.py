from bs4 import BeautifulSoup
import sqlite3
import requests

def get_celebrity_airplanes():
    url = "https://celebrityprivatejettracker.com/#gref"


    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    parentspan = soup.findAll('span', class_="tooltipa")


    celeb_list = []
    # for each in parentspan:
    #     name_tag = each.find('a', class_="maincolor")
    #     unwanted_entries = {"PST", "EST", "CST", "MST", ""}
    #     if not name_tag or name_tag.text.strip() in unwanted_entries:
    #             continue 
    #     name = name_tag.text.strip()
    unwanted_entries = {"PST", "EST", "CST", "MST", "", "Bahamas"}  # Skip unwanted names

    for each in parentspan:
        # Get the name
        name_tag = each.find('a', class_="maincolor")
        if not name_tag:  # Skip if name_tag is None
            continue
        name = name_tag.text.strip()

        # Skip unwanted entries
        if name in unwanted_entries:
            continue
            
        plane_info = name_tag.find_next(text=True)  
        plane_name = plane_info.find_next(text=True).strip() if plane_info else None  

        if plane_name and '(' in plane_name:
            plane_name = plane_name.split('(')[0].strip()  


        tailnumber_tag = name_tag.find_next("a", href=True)
        if tailnumber_tag:
            tail_number = tailnumber_tag.text.strip() 
        else:
            tail_number = None

        celeb_list.append({
                "name": name,
                "plane": plane_name,
                "tailnumber": tail_number
                
            })
    return celeb_list





def insertcelebtable(celeb_list):

    conn = sqlite3.connect('celebrity_airplane.db')  # Creates or connects to a database
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Airplane')

    for celeb in celeb_list:
        cursor.execute('''
            INSERT INTO Airplane (celebname, planename, tail_number)
            VALUES (?, ?, ?)
        ''', (celeb['name'], celeb['plane'], celeb['tailnumber']))
    
    conn.commit()
    conn.close()

celeb_list = get_celebrity_airplanes()
insertcelebtable(celeb_list)


    