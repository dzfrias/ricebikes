from flask import Flask
from routes.transactions import bp as transactions_bp


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello world"

    app.register_blueprint(transactions_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
