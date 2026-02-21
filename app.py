from flask import Flask
from routes.transactions import bp as transactions_bp
from routes.pages import bp as pages_bp


def create_app() -> Flask:
    """
    Create the RiceBikes app.

    NOTE: this function can be extended later to have parameters. This could allow build-time
    parameters to be specified (such as prod vs dev builds).
    """
    app = Flask(__name__)

    app.register_blueprint(transactions_bp)
    app.register_blueprint(pages_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
