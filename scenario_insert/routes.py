from datetime import datetime

from flask import Blueprint, render_template, current_app, request, redirect

from sql_provider import SQL_Provider
from database import work_with_db, work_with_db_insert
from access import group_permission_decorator

insert_app = Blueprint('insert', __name__, template_folder='templates')
provider = SQL_Provider('sql/')


@insert_app.route('/')
@group_permission_decorator
def insert():
    return render_template('insert.html')


@insert_app.route('/client', methods=['GET', 'POST'])
def client():
    if request.method == 'GET':
        data = ["ФИО клиента", "Номер телефона клиента"]
        return render_template('add_client.html', data=data)
    else:
        name = request.form.get('name', None)
        phone = request.form.get('phone', None)
        try:
            check_correct_type_name = name.replace(" ", "").isalpha()
            int(phone.replace('-', "").replace('+', ""))
        except ValueError:
            return render_template("incorrect_type_parametres.html")
        finally:
            if not check_correct_type_name:
                return render_template("incorrect_type_parametres.html")

        if name is not None and phone is not None:
            sql = provider.get('fetch_client.sql', name=name.strip(), phone=phone.strip())
            res = work_with_db(current_app.config['dbconfig'], sql)
            if res:
                data = ["ФИО клиента", "Номер телефона клиента"]
                return render_template("client_already_insert_in_DB.html", data=data, res=res)
            sql = provider.get('insert_client.sql', name=name.strip(), phone=phone.strip())
            work_with_db_insert(current_app.config['dbconfig'], sql)
            sql = provider.get('fetch_client.sql', name=name.strip(), phone=phone.strip())
            res = work_with_db(current_app.config['dbconfig'], sql)
            if res:
                data = ["ФИО клиента", "Номер телефона клиента"]
                return render_template("insert_client_done.html", data=data, res=res)
            else:
                return render_template('failed.html')
        else:
            return render_template('failed.html')


@insert_app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'GET':
        sql = provider.get('select_name_users_without_orders.sql')
        names = work_with_db(current_app.config['dbconfig'], sql)
        return render_template('insert_input_order.html', names=names)
    else:
        id = request.form.get('id', None)
        if id is not None:
            sql = provider.get('sql_insert_order.sql', id=id)
            work_with_db_insert(current_app.config['dbconfig'], sql)
            sql = provider.get('fetch_information_about_cur_client.sql', ar_id=id)
            res = work_with_db(current_app.config['dbconfig'], sql)

            result = [res[0]['name'], res[0]['telephone'], str(datetime.now().strftime("%Y.%m.%d"))]
            data = ["ФИО клиента", "Телефон клиента", "Дата оформления договора"]
            return render_template('success_insert.html', data=data, result=result)

        return render_template('failed.html')


@insert_app.route('/bilboards', methods=['GET', 'POST'])
def bilboards():
    if request.method == 'GET':
        sql = provider.get('bilboards.sql')
        res = work_with_db(current_app.config['dbconfig'], sql)
        data = ["Размер билборда", "Адрес размещения", "Суточная стоимость размещения", "Действие"]
        return render_template('bilboards.html', result=res, data=data)
    else:
        bil_id = request.form.get('bil_id')
        sql = provider.get('bilboards_delete.sql', idBil=bil_id)
        work_with_db_insert(current_app.config['dbconfig'], sql)
        return redirect('/insert/bilboards')


@insert_app.route('/bilboards/add', methods=['GET', 'POST'])
def bilboards_add():
    if request.method == 'GET':
        data = ["Размер билборда", "Адрес размещения", "Суточная стоимость размещения"]
        return render_template('fill_cells.html', data=data)

    else:
        size = request.form.get('size')
        address = request.form.get('address')
        cost = request.form.get('cost')
        if size and address and int(cost):
            sql = provider.get('insert_bilboards.sql', size=size, address=address, cost=cost)
            work_with_db_insert(current_app.config['dbconfig'], sql)
            return redirect('/insert/bilboards')
        else:
            return render_template('failed.html')
