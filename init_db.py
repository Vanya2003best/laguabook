import os
import sys

# Добавляем корневой каталог проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from app.models import db


def create_minimal_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Убедитесь, что директория instance существует
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    return app


if __name__ == "__main__":
    app = create_minimal_app()
    with app.app_context():
        db.create_all()
        print(f"База данных создана успешно в {os.path.join(app.instance_path, 'app.db')}")