import os
from flask import Flask, render_template
from app.config import Config
from app.extensions import db, login_manager, mail, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Ensure folders exist ──────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # ── Initialise extensions ─────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # ── Register blueprints ───────────────────────────────
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.customer import customer_bp
    app.register_blueprint(customer_bp)

    # ── Error handlers ────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # ── Create database tables ────────────────────────────
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    # ── CLI: create admin (safe way to add admins) ────────
    @app.cli.command('create-admin')
    def create_admin():
        """Create an admin account from the terminal."""
        import click
        from app.models import User
        username = click.prompt('Admin username')
        email = click.prompt('Admin email')
        password = click.prompt('Admin password', hide_input=True,
                                confirmation_prompt=True)

        if User.query.filter_by(email=email).first():
            click.echo('Error: Email already registered.')
            return
        if User.query.filter_by(username=username).first():
            click.echo('Error: Username already taken.')
            return

        user = User(username=username, email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin "{username}" created successfully!')

    return app
