from flask import Flask, request
from routes.transactions import bp as transactions_bp


DATE_FORMAT = "%Y-%m-%d"


app = Flask(__name__)


@app.route("/")
def index():
    return "Hello world"


app.register_blueprint(transactions_bp)

if __name__ == "__main__":
    app.run()
