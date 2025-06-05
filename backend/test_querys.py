import sqlite3

DB_FILE = "users.db"

def ver_usuarios():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    col_names = [description[0] for description in cur.description]
    conn.close()

    print("Usuarios registrados:")
    for row in rows:
        for name, value in zip(col_names, row):
            print(f"{name}: {value}", end=" | ")
        print()  # Nueva línea por usuario

if __name__ == "__main__":
    ver_usuarios()