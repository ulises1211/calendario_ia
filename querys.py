import sqlite3

DB_FILE = "users.db"

def ver_usuarios():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    conn.close()

    print("Usuarios registrados:")
    for row in rows:
        print(f"ID: {row[0]} | Nombre: {row[1]} | Email: {row[2]} | WhatsApp: {row[3]}")

if __name__ == "__main__":
    ver_usuarios()
