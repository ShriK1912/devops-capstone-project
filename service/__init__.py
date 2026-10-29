import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_talisman import Talisman

from service.models import db
from service.routes import accounts


def _configured_origins(origins):
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "local-development-key"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///accounts.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        FORCE_HTTPS=os.getenv("FORCE_HTTPS", "false").lower() == "true",
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", "http://localhost:3000"),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    Talisman(
        app,
        force_https=app.config["FORCE_HTTPS"],
        content_security_policy={"default-src": "'self'"},
    )
    CORS(
        app,
        resources={
            r"/accounts*": {"origins": _configured_origins(app.config["CORS_ORIGINS"])}
        },
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    app.register_blueprint(accounts)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    with app.app_context():
        db.create_all()

    return app
