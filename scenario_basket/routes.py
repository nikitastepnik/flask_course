import datetime

from flask import Blueprint, render_template, current_app, request, session, redirect

from sql_provider import SQL_Provider
from database import work_with_db, work_with_db_transact
from .utils import add_to_basket, clear_basket
from access import group_permission_decorator

basket_app = Blueprint('basket', __name__, template_folder='templates')
provider = SQL_Provider('sql/')


@basket_app.route('/', methods=['GET', 'POST'])
@group_permission_decorator
def select_customer():
    if request.method == 'GET':
        session['id_client'] = 0
        session['basket'] = []
        session['name'] = 0
        db_config = current_app.config['dbconfig']
        session['bilboards'] = []
        sql = provider.get('select_name_users_with_contracts.sql')
        names = work_with_db(db_config, sql)
        return render_template('select_customer.html', names=names)


@basket_app.route('/order', methods=['GET', 'POST'])
def list_orders():
    if not session['id_client']:
        try:
            session['id_client'] = request.url.split('=')[1]
        except IndexError:
            return render_template('fail_with_name.html')

    db_config = current_app.config['dbconfig']
    select_name_client = provider.get('select_name_user.sql', ar_id=session['id_client'])
    name = work_with_db(db_config, select_name_client)
    session['name'] = name[0]['name']
    if request.method == 'GET':
        basket = session.get('basket', [])
        sql = provider.get('order_list.sql')
        items = work_with_db(db_config, sql)
        return render_template('basket_order_list.html', basket=basket, items=items, name=session['name'])
    else:
        dates = [request.form.get('date_start', None), request.form.get('date_end', None)]
        item_id = request.form['idBil']
        bilboards = session.get('bilboards', [])
        bilboard = {item_id: [dates[0], dates[1]]}
        if dates[0] == '' or dates[1] == '' or (dates[0] > dates[1]) or (dates[0] == dates[1]):
            return redirect('/basket/order')
        else:
            flag = check_correct_date(bilboards, item_id, dates)
            if not flag:
                return redirect('/basket/order')

            bilboards.append(bilboard)
            session['bilboards'] = bilboards
            sql = provider.get('order_item.sql', item_id=item_id)
            items = work_with_db(db_config, sql)
            if items:
                items[0]["date_start"] = dates[0]
                items[0]["date_end"] = dates[1]
                sql = provider.get('find_or_id.sql', ar_id=session['id_client'])
                or_id = work_with_db(db_config, sql)
                items[0]["or_id"] = or_id[0]['or_id']
                add_to_basket(items[0])
                return redirect('/basket/order')
            else:
                return render_template('no_item.html')


@basket_app.route('/clear-basket')
def clear_basket_handler():
    clear_basket()
    return redirect('/basket/order')


@basket_app.route('/buy')
def buy_basket_handler():
    db_config = current_app.config['dbconfig']
    current_basket = session.get('basket', [])
    failed_bilboards = []
    successful_bilboards = []
    #  For each billboard checks for availability to rent in given range date
    for item in current_basket:
        sql_check_availability = provider.get('check_availability_bilboard.sql', date_start=item['date_start'],
                                              date_end=item['date_end'],
                                              bil_id=item['idBil'])
        res = work_with_db(db_config, sql_check_availability)
        if not res:  # Check the availability of a billboard in a given period of time among previously placed orders
            sql_add = provider.get('insert_order_table.sql', date_start=item['date_start'], date_end=item['date_end'],
                                   bil_id=item['idBil'], ord_id=item['or_id'])
            procedure = provider.get('procedure_order.sql', ord_id=item['or_id'])
            work_with_db_transact(db_config, sql_add, procedure)
            successful_bilboards.append(item)
        else:
            for i in range(len(res)):
                res[i]['cost'] = item['cost']
                res[i]['address'] = item['address']
                res[i]['date_start'] = str(res[i]['date_start'])
                res[i]['date_end'] = str(res[i]['date_end'])
                failed_bilboards.insert(i, res[i])
    clear_basket()
    return render_template('order_done.html', basket=successful_bilboards, not_basket=failed_bilboards,
                           name=session['name'])


def convert_datetime(string):  # Convert format string to datetime.date
    date = string.split('-')
    return datetime.date(int(date[0]), int(date[1]), int(date[2]))


def check_correct_date(bilboards, item_id, dates):
    """
    Check whether if it is possible to rent a bilboard
    within a given date period.
    It is impossible if in basket already located added bilboard in the
    same date period
    :param bilboards: Current bilboards in basket
    :param item_id:   Unique id of added bilboard
    :param dates:     List of dates [date_start; date_end]
    :return:          Return 0 if n basket already located added bilboard in the
                      same date period.
                      Return 1 otherwise
    """
    for item in bilboards:
        dates_others = []
        try:
            dates_others = item[item_id]
        except KeyError:
            pass
        if dates_others:
            date_start = convert_datetime(dates_others[0])
            date_end = convert_datetime(dates_others[1])
            if ((date_start < convert_datetime(dates[0]) < date_end) or (
                    date_start < convert_datetime(dates[1]) < date_end)):
                return 0
    return 1
