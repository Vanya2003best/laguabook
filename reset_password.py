# reset_password.py
import sqlite3
from werkzeug.security import generate_password_hash

# Подключение к базе данных
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Новый пароль
new_password = "123456"
username = "student-wroclaw"

# Хешируем пароль
hashed_password = generate_password_hash(new_password)

# Обновляем пароль в базе данных
cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?",
               (hashed_password, username))
conn.commit()

# Проверяем, был ли обновлен пароль
if cursor.rowcount > 0:
    print(f"Пароль для '{username}' успешно обновлен на '{new_password}'")
else:
    print(f"Пользователь '{username}' не найден")

conn.close()