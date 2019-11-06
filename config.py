import os
import json

class Config(object):
    # Определяет, включен ли режим отладки
    # В случае если включен, flask будет показывать
    # подробную отладочную информацию. Если выключен -
    # - 500 ошибку без какой либо дополнительной информации.
    DEBUG = False
    # Включение защиты против "Cross-site Request Forgery (CSRF)"
    CSRF_ENABLED = True
    # Случайный ключ, которые будет исползоваться для подписи
    # данных, например cookies.
    SECRET_KEY = 'YOUR_RANDOM_SECRET_KEY'
    # URI используемая для подключения к базе данных
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SEND_FILE_MAX_AGE_DEFAULT = 0

    # Языковые настройки
    PATH_LANGFIELDS = os.path.join(os.getcwd(), "langfields.json")
    PATH_SURVEYS = os.path.join(os.getcwd(), "surveys.json")
    PATH_DERM_DISEASES = os.path.join(os.getcwd(), "derm_diseases.json")
    LANG = "en"
    with open(PATH_LANGFIELDS, "r+", encoding="utf-8") as json_file:
        LANGFIELDS = json.load(json_file)[LANG]

    with open(PATH_SURVEYS, "r+", encoding="utf-8") as json_file:
        SURVEYS = json.load(json_file)[LANG]

    UPLOAD_FOLDER = os.path.join(os.getcwd(),
                                 "app",
                                 "static",
                                 "files")


class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True