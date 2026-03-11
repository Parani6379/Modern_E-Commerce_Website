import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))


class Config:
    # ── Core ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # ── Database ──────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'girlhub.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Upload ────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ── Flask-Mail (Gmail SMTP) ───────────────────────────
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # ── Owner email (receives order notifications) ────────
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

    # ── Pagination ────────────────────────────────────────
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 15
    EXPENSES_PER_PAGE = 15
