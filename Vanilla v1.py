
import sqlite3
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

def log():
    """ Checking if username is registered.

    """
    log = ''
    users = ["kVz", "Skrioo"]

    while log not in users:
        log = input("Username? ")
        if log not in users:
            print("Invalid username.")
        else:
            break

    return log

def provera(conn, logi):
    sql = ''' SELECT UnosBr, Ime, VremeUlaza, VremeIzlaza
                FROM Unosi''' # Citanje unosa u tabeli Unosi
    cur = conn.cursor()
    cur.execute(sql)
    unosi = cur.fetchall()
    now = datetime.now()
    now_str = now.strftime("%d/%m/%y %H:%M")
    nista = ["", None]
    
    sql2 = '''UPDATE Unosi
              SET VremeIzlaza = ?, 
                  Pauza = ?
              WHERE UnosBr = ?''' # Unosenje vremena logouta i vremena pauze u tabelu Unosi

    sql3 = '''INSERT INTO Materijal(UnosBr, Radjeno, Detalji)
              VALUES(?,?,?)'''  # Unosenje podataka o terminu u tabelu Materijali
    
    sql4 = '''INSERT INTO Unosi(UnosBr,Ime,VremeUlaza)
              VALUES(?,?,?)'''  # Novi unos za login

    lista_unosa = []
    for unos in unosi:
        if unos[3] in nista and unos[1] == logi:
            for delovi in unos:
                lista_unosa.append(delovi)

    if len(lista_unosa) < 4:
        cur.execute(sql4, (unosi[-1][0]+1, logi, now_str))
        print(
            f"Dobrodosao {logi}.\nVreme pocetka: {now_str}\nZelim vam ugodno programiranje!")
        conn.commit()
        log_in = True
        return log_in
    
    for unos in unosi:
        if unos[3] in nista and unos[1] == logi:
            # Treba da te pita sta si radio, detalje i kolika je bila pauza
            jezik = input("Koji jezik ?  ")
            detalji = input("Reci nam malo o tome:  ")
            pauza = input("A koliko si pauzirao ? (Format: HH:MM)  ")
            cur.execute(sql2, (now_str, pauza, unos[0]))
            cur.execute(sql3, (unos[0], jezik, detalji))
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
    # Konvertovanje vremena ulaza u datetime format
    vreme_ulaza_str = vreme_tup[0]
    vreme_ulaza = datetime.strptime(vreme_ulaza_str, '%d/%m/%y %H:%M')

    # Konvertovanje vremena izlaza u datetime format
    vreme_izlaza_str = vreme_tup[1]
    vreme_izlaza = datetime.strptime(vreme_izlaza_str, '%d/%m/%y %H:%M')

    # Odredjivanje timedelta od ulaza do izlaza
    trajanje = vreme_izlaza - vreme_ulaza

    # Konvertovanje rezultata iz timedelta u string pa u tuple
    bez_pauze_str = str(trajanje)
    nista = ['', None, 0]

  # Petlja za proveru da li postoji pauza i ako postoji da je oduzme
    vreme_pauza_str = vreme_tup[2]
    if vreme_pauza_str not in nista:
        # Konvertovanje timedelte u datetime format i oduzimanje pauze
        trajanje_str = str(trajanje)
        trajanje = datetime.strptime(trajanje_str, '%H:%M:%S')
        vreme_pauza = datetime.strptime(vreme_pauza_str, '%H:%M')
        # Konvertovanje rezultata u string pa u tuple
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
    logi = log()
    unos_br = provera(conn, logi)

    if log_in == False:
        with conn:
            update_task(conn, unos_br)


if __name__ == '__main__':
    main()
