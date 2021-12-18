from flask import Blueprint, session, render_template, request, current_app

from access import group_permission_decorator
from sql_provider import SQL_Provider
from database import work_with_db

auth_app = Blueprint('auth', __name__, template_folder='templates')
provider = SQL_Provider('sql/')


@auth_app.route('/login', methods=['GET', 'POST'])
@group_permission_decorator
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            sql = provider.get('get_group_user.sql', login=login, password=password)
            result = work_with_db(current_app.config['dbconfig'], sql)
            if result:
                session['group_name'] = result[0]['group']
                return render_template('success.html', login=login)
            else:
                return render_template('invalid_login_or_password.html')

