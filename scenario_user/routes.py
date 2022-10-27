from flask import Blueprint, render_template, current_app, request

from access import group_permission_decorator
from database import work_with_db, work_with_db_insert
from sql_provider import SQL_Provider

user_app = Blueprint('user_app', __name__, template_folder='templates')
provider = SQL_Provider('sql/')


@user_app.route('/')
@group_permission_decorator
def user_index():
    return render_template('menu.html')


@user_app.route('/sql1', methods=['GET', 'POST'])
def user_sql1():
    if request.method == 'GET':
        return render_template('user_input1.html')
    else:
        cost = request.form.get('cost', None)
        try:
            sql = provider.get('sql1.sql', val=cost)
            result = work_with_db(current_app.config['dbconfig'], sql)
            data = ["Размер билборда", "Адрес размещения", "Суточная стоимость размещения"]
            if not result:
                return render_template('void.html')
            return render_template('table1.html', data=data, result=result, cost=cost)
        except ValueError:
            return render_template('incorrect_type_parametres.html')


@user_app.route('/sql2', methods=['GET', 'POST'])
def user_sql2():
    if request.method == 'GET':
        sql = provider.get('fetch_size_bilboards.sql')
        sizes = work_with_db(current_app.config['dbconfig'], sql)
        return render_template('user_input2.html', sizes=sizes)
    else:
        size = request.form.get('size', None)
        if size is not None:
            sql = provider.get('sql2.sql', val=size)
            result = work_with_db(current_app.config['dbconfig'], sql)
            data = ["Размер", "Адрес размещения", "Суточная стоимость размещения"]
            if not result:
                return render_template('void.html')
            return render_template('table2.html', data=data, result=result, size=size)
        else:
            return render_template('void.html')


@user_app.route('/sql3', methods=['GET', 'POST'])
def user_sql3():
    if request.method == 'GET':
        sql = provider.get('select_name_users.sql')
        names = work_with_db(current_app.config['dbconfig'], sql)
        return render_template('user_input3.html', names=names)
    else:
        id = request.form.get('id', None)
        if id is not None:
            sql = provider.get('sql3.sql', id=id)
            result = work_with_db(current_app.config['dbconfig'], sql)
            data = ["Имя/Фамилия", "Дата заключения договора долгосрочной аренды", "Моб. телефон"]
            if not result:
                return render_template('void.html')
            sql = provider.get('select_name_user.sql', ar_id=id)
            name = work_with_db(current_app.config['dbconfig'], sql)
            return render_template('table3.html', result=result, data=data, name=name[0]['name'])
        else:
            return render_template('void.html')


@user_app.route('/total_amount', methods=['GET', 'POST'])
def user_sql4():
    if request.method == 'GET':
        sql = provider.get('select_name_users_with_orders.sql')
        names = work_with_db(current_app.config['dbconfig'], sql)
        return render_template('user_input4.html', names=names)
    else:
        arend_id = request.form.get('id', None)
        sql = provider.get('find_or_id.sql', ar_id=arend_id)
        or_id = work_with_db(current_app.config['dbconfig'], sql)
        if or_id:
            sql1 = provider.get('procedure_order_fetch.sql', num_ord=or_id[0]['or_id'])
            res1 = work_with_db(current_app.config['dbconfig'], sql1)
            sql2 = provider.get('procedure_order_str_fetch.sql', num_ord=or_id[0]['or_id'])
            res2 = work_with_db(current_app.config['dbconfig'], sql2)
            data1 = ["Номер билборда", "Дата начала аренды", "Дата окончания аренды", "Стоимость за период"]
            data2 = ["Номер заказа", "Общая стоимость"]
            if res1 is None or res2 is None:
                return render_template('void.html')
            sql = provider.get('select_name_user.sql', ar_id=arend_id)
            name = work_with_db(current_app.config['dbconfig'], sql)
            return render_template('table4.html', res1=res1, res2=res2, data1=data1, data2=data2, name=name[0]['name'])
        else:
            return render_template('void.html')
