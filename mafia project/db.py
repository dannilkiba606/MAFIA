from sqlite3 import *
from random import shuffle

def insert_player(player_id, username):
    con = connect("db.db")
    cur = con.cursor()
    sql = f"INSERT INTO players (player_id, username) VALUES ('{player_id}', '{username}')"
    cur.execute(sql)
    con.commit()
    con.close()

def players_amount():
    con = connect("db.db")
    cur = con.cursor()
    sql = f"SELECT * FROM players"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    return len(res)

def get_mafia_usernames():
    con = connect("db.db")
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE role='mafia'"
    cur.execute(sql)
    data = cur.fetchall()
    names = ''
    for row in data:
        name = row[0]
        names += name + '\n'
    con.close()
    return names

def get_addl_usernames(players):
    con = connect("db.db")
    cur = con.cursor()

    sql = f"SELECT username FROM players WHERE role='doctor'"
    cur.execute(sql)
    doctor = cur.fetchone()

    sql = f"SELECT username FROM players WHERE role='sheriff"
    cur.execute(sql)
    sherrif = cur.fetchone()

def get_players_roles():
    con = connect("db.db")
    cur = con.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data

def get_alive():
    con = connect("db.db")
    cur = con.cursor()   
    sql = "SELECT username FROM players WHERE dead = 0"
    cur.execute(sql)
    data = cur.fetchall()
    new_data = [row[0] for row in data]
    return new_data

def get_players_id():
    con = connect("db.db")
    cur = con.cursor()
    sql = "SELECT player_id FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    all_id = [row[0] for row in data]
    return all_id

def set_roles(players):
    game_roles = ['citizen'] * players
    if players >= 4:
        game_roles[-1] = 'doctor'
    if players >= 6:
        game_roles[-2] = 'sheriff'
    mafias = int(players * 0.3)
    for i in range(mafias):
        game_roles[i] = 'mafia'
    shuffle(game_roles)

    con = connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT player_id FROM players")
    player_ids_rows = cur.fetchall()
    for role, row in zip(game_roles, player_ids_rows):
        sql = f"UPDATE players SET role = '{role}' WHERE player_id = {row[0]}"
        cur.execute(sql)
    con.commit()
    con.close()

def vote(type, username, player_id):
    con = connect("db.db")
    cur = con.cursor
    sql = (f"SELECT username FROM players WHERE player_id = {player_id} AND dead = 0 AND voted = 0")
    cur.execute(sql)
    voters = cur.fetchone()
    if voters:
        sql = (f"UPDATE players SET {type} = {type} + 1 WHERE username = '{username}'")
        cur.execute(sql)
        sql = (f"UPDATE players SET voted = 1 WHERE player_id = '{player_id}'")
        cur.execute(sql)

        con.commit()
        con.close()
        return True
    con.close()
    return False

def mafia_kill():
    con = connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE dead = 0 AND role = 'mafia'")
    mafia_alive = cur.fetchone()[0]
    username_killed = ''

    if max_votes == mafia_alive:
        cur.execute(f"SELECT username FROM players WHERE mafia_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}'")
        con.commit()
    con.close()
    return username_killed

def citizens_kill():
    con = connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}")
    max_votes_count = cur.fetchone()[0]
    username_killed = ''

    if max_votes_count == 1:
        cur.execute(f"SELECT username FROM players WHERE citizen_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}'")
        con.commit()
    con.close()
    return username_killed

def clear(dead = False):
    con = connect("db.db")
    cur = con.cursor()
    sql = f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, voted = 0"
    if dead:
        sql += ", dead = 0"
    cur.execute(sql)
    con.commit()
    con.close()

def check_winner():
    con = connect("db.db")
    cur = con.cursor()

    mafia_players = 0
    citizen_players = 0

    sql = f"SELECT role FROM players WHERE dead = 0"
    cur.execute(sql)

    data = cur.fetchall()
    roles = list()
    for role in data:
        roles.append(role[0])

    for role in roles:
        if role == 'mafia':
            mafia_players += 1
        else:
            citizen_players += 1

    if mafia_players >= citizen_players:
        return "Мафия"
    if mafia_players == 0:
        return "Горожане"

    con.commit()
    con.close()