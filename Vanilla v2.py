#Unosenje vremena rada u tabelu materijali, po broju unosa.
#Oduzimanje pauze.

import sqlite3
import bcrypt
import random
from sqlite3 import Error
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def log(conn):
    
    # Globali (u sklopu funkcije)
    log = 'otac'
    users = []
    log_hash = "gasgsaasffsadsa"
    pass_check = "asdadsa"
    reg_pass = "pass"
    reg_ans = ["yes", "Yes", "y", "Y", "YES"]
    new_user = False
    
    sql = ''' SELECT UserID, Ime, Password
                FROM Users'''
    sql3 = '''INSERT INTO Users(UserID, Ime, Password)
              VALUES(?,?,?)'''
    
    cur = conn.cursor()
    cur.execute(sql)
    useri = cur.fetchall()
    
    for user in useri: # Iterovanje usera
        user1 = user[1]
        users.append(user1)
    
    
    
    while log not in users: # Petlja koja proverava log in, ako nije log in u pitanju salje na register.
        log = input("Username? ") 
        if log not in users:
            print("Unable to find user. Do you want to register ?")
            reg_check = input("Y/N? ")
            if reg_check in reg_ans: # Razdvajanje da li hoce user da se registruje ili ne
                new_user = True
                break
            else:
                log_in = True # U slucaju da nece da se registruje, ovaj kod zatvara skriptu.
                return log_in
        for user in useri: # Petlja koja trazi koji user pokusava log in.
            if user[1] == log:
                while pass_check != True: # Petlja za proveravanje passworda
                    log_pass = input("Password? ")
                    log_hash = bcrypt.hashpw(log_pass.encode(), bcrypt.gensalt()) 
                    pass_check = bcrypt.checkpw(log_pass.encode(), log_hash)
                    if pass_check != True:
                        print("Wrong password, try again please.")
                    else:
                        return log
                    
    
    
    if new_user == True: # Registracija
        reg_inp = input("Enter your username: ")
        while len(reg_pass) < 8: 
            reg_pass = input("Enter your password: ")
            if len(reg_pass) < 8:
                print("Password must be atleast 8 characters long.")
            else:
                if len(reg_pass) >= 8: # Enkripcija passworda
                    pass_hash = bcrypt.hashpw(reg_pass.encode(), bcrypt.gensalt())
                    break
        
        if reg_inp != int and len(reg_pass) >= 8: # Unosenje passworda u tabelu
            user_id = random.randrange(10**5, 10**6)
            cur = conn.cursor()
            cur.execute(sql3, (user_id, reg_inp, pass_hash)) # Unosesnje Username-a, UserID-a i passworda u tabelu
            conn.commit()
            print(f"Postovani {reg_inp} uspesno ste se registrovali. Bilo nam je cast sa vama poslovat.")
            print("Da li zelite da se logujete ? ")
            log_in_check = input("Y/N? ")
            if log_in_check in reg_ans:
                log_in = False
                return log_in
            else:
                log_in = True
                return log_in
              
def provera(conn, logi):
    
    sql0 = ''' SELECT UserID, Ime
                FROM Users'''
    sql = ''' SELECT UnosBr, Ime, VremeUlaza, VremeIzlaza
                FROM Unosi'''
    cur = conn.cursor()
    cur.execute(sql)
    unosi = cur.fetchall()
    now = datetime.now()
    now_str = now.strftime("%d/%m/%y %H:%M")
    
    nista = ["", None]
    users = []
    
    cur.execute(sql0)
    useri = cur.fetchall()
    for user in useri:
        user1 = user[1]
        users.append(user1)
    

    sql2 = '''UPDATE Unosi
              SET VremeIzlaza = ?, 
                  Pauza = ?
              WHERE UnosBr = ?'''

    sql3 = '''INSERT INTO Materijal(UnosBr, Radjeno, Detalji)
              VALUES(?,?,?)'''
    sql4 = '''INSERT INTO Unosi(UnosBr,Ime,VremeUlaza)
              VALUES(?,?,?)''' #Novi unos za login
    
    if unosi[-1][3] not in nista:
        cur.execute(sql4, (unosi[-1][0]+1, logi, now_str)) #sql4 kod bi trebao da bude pravljenje novog unosa u tabelu na osnovu usernamea
        print(f"Dobrodosli {logi}.\nVreme pocetka: {now_str}\nZelim vam ugodno programiranje!")
        conn.commit()
        log_in = True
        return log_in
    elif logi != unosi[-1][1]:
        cur.execute(sql4, (unosi[-1][0]+1, logi, now_str)) #sql4 kod bi trebao da bude pravljenje novog unosa u tabelu na osnovu usernamea
        print(f"Dobrodosli {logi}.\nVreme pocetka: {now_str}\nZelim vam ugodno programiranje!")
        conn.commit()
        log_in = True
        return log_in
    #Ova petlja provera je li user vec ulogovan i ako jeste da ga izloguje a ako nije da pravi novi unos
    for unos in unosi:
        if unos[3] in nista and logi in users:
            #Treba da te pita sta si radio, detalje i kolika je bila pauza
            jezik = input("Koji jezik bate ?  ")
            detalji = input("Reci nam malo o tome:  ")
            pauza = input("A koliko si pauzirao ? (Format: HH:MM)  ")
            cur.execute(sql2, (now_str, pauza, unos[0]))
            cur.execute(sql3, (unos[0],jezik, detalji))
            conn.commit()
            unos_br = unos[0]
            
            return unos_br      


def update_task(conn, unos_br):
    """
    update VremeRada 
    :param conn:
    :param task:
    :return: UnosBr
    """
    sql1 = ''' SELECT VremeUlaza, VremeIzlaza, Pauza
                FROM Unosi
                WHERE UnosBr = ?'''
    cur = conn.cursor()
    cur.execute(sql1, (unos_br,))
    vreme_tup = cur.fetchall()[0]   
    #Konvertovanje vremena ulaza u datetime format
    vreme_ulaza_str = vreme_tup[0]
    vreme_ulaza = datetime.strptime(vreme_ulaza_str, '%d/%m/%y %H:%M')
  
    #Konvertovanje vremena izlaza u datetime format      
    vreme_izlaza_str = vreme_tup[1]
    vreme_izlaza = datetime.strptime(vreme_izlaza_str, '%d/%m/%y %H:%M')

    #Odredjivanje timedelta od ulaza do izlaza
    trajanje = vreme_izlaza - vreme_ulaza
  
    #Konvertovanje rezultata iz timedelta u string pa u tuple
    bez_pauze_str = str(trajanje)
    bez_pauze_tupl = (bez_pauze_str,)

  
  #Petlja za proveru da li postoji pauza i ako postoji da je oduzme
    vreme_pauza_str = vreme_tup[2]
    if vreme_pauza_str != None and vreme_pauza_str != '':
        #Konvertovanje timedelte u datetime format i oduzimanje pauze
        trajanje_str = str(trajanje)
        trajanje = datetime.strptime(trajanje_str, '%H:%M:%S')  
        vreme_pauza = datetime.strptime(vreme_pauza_str, '%H:%M')
        #Konvertovanje rezultata u string pa u tuple
        sa_pauzom_str = str(trajanje - vreme_pauza)
        vreme = sa_pauzom_str
    else:
        vreme = bez_pauze_str

    
    sql2 = ''' UPDATE Materijal
              SET VremeRada = ?
              WHERE UnosBr = ?'''
    cur.execute(sql2, (vreme, unos_br))
    conn.commit()

def main():
    database = r"100 day challenge.db"

    # create a database connection
    
    conn = create_connection(database)
    log_in = False
    while log_in == False:
        logi = log(conn)
        log_in = logi
    if logi != False and logi != True:
        unos_br = provera(conn, logi)
        if log_in == False:
            with conn:
                update_task(conn, unos_br)
    else:
        print("Ok, ugodan dan vam zelim")

    conn.close()
if __name__ == '__main__':
    main()

