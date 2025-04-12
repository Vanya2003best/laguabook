# view_db.py
import os
import sys
import sqlite3

# Путь к базе данных
db_path = os.path.join('instance', 'app.db')

if not os.path.exists(db_path):
    print(f"База данных не существует по пути: {db_path}")
    sys.exit(1)

# Подключение к базе данных
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Таблицы в базе данных:")
for table in tables:
    print(f"- {table[0]}")

# Если есть таблица пользователей, выведем её содержимое
if ('users',) in tables:
    cursor.execute("SELECT id, username, length(username) as name_length, email FROM users")
    users = cursor.fetchall()

    print("\nПользователи (с длиной имени):")
    for user in users:
        print(f"ID: {user[0]}, Username: '{user[1]}', Длина: {user[2]}, Email: {user[3]}")
else:
    print("\nТаблица пользователей не найдена!")

conn.close()