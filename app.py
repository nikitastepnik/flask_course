import json

from flask import Flask, render_template, session

from scenario_insert.routes import insert_app
from sql_provider import SQL_Provider
from scenario_user.routes import user_app
from access import group_permission_decorator
from scenario_auth.routes import auth_app
from scenario_basket.routes import basket_app

app = Flask(__name__)

app.register_blueprint(user_app, url_prefix='/user')
app.register_blueprint(auth_app, url_prefix='/auth')
app.register_blueprint(insert_app, url_prefix='/insert')
app.register_blueprint(basket_app, url_prefix='/basket')
app.config['dbconfig'] = json.load(open('configs/db.json', 'r'))
app.config['ACCESS_CONFIG'] = json.load(open('configs/access.json', 'r'))

app.config['SECRET_KEY'] = 'my_secret_key'
provider = SQL_Provider('sql/')


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/logout')
@group_permission_decorator
def clear_session():
    # if 'counter' in session:
    #     session.pop('counter')
    session.clear()
    return render_template('logout.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
