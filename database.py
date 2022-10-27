import traceback
from pymysql import connect
from pymysql.err import InterfaceError
from pymysql.err import OperationalError
from pymysql.err import ProgrammingError


class UserDatabase:

    def __init__(self, config: dict):
        self.config = config

    def __enter__(self):
        try:
            self.conn = connect(**self.config)
            self.cursor = self.conn.cursor()
            return self.cursor
        except OperationalError as err:
            if err.args[0] == 1045:
                print('Неверный логин и пароль, повторите подключение')
                return None
            if err.args[0] == 2003:
                print('Неверно введен порт или хост для подключения к серверу')
                return None
            if err.args[0] == 1049:
                print('Такой базы данных не существует')
                return None
        except UnicodeEncodeError as err:
            print('Были введены символы на русском языке')
            return None
        except InterfaceError as err:
            return err

    def __exit__(self, exc_type, exc_value, exc_trace):
        if exc_value:
            if exc_value == 'Курсор не был создан':
                print('Курсор не создан')
            elif exc_value.args[0] == 1064:
                print('Синтаксическая ошибка в запросе!')
            elif exc_value.args[0] == 1146:
                print('Ошибка в запросе! Такой таблицы не существует.')
            elif exc_value.args[0] == 1054:
                print('Ошибка в запросе! Такого поля не существует.')
            return False
        else:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            return True


def work_with_db(dbconfig: dict, _SQL: str) -> list:
    result = []
    with UserDatabase(dbconfig) as cursor:
        cursor.execute(_SQL)
        schema = [column[0] for column in cursor.description]
        for item in cursor.fetchall():
            result.append(dict(zip(schema, item)))
    return result


def work_with_db_insert(dbconfig: dict, _SQL: str) -> list:
    with UserDatabase(dbconfig) as cursor:
        cursor.execute(_SQL)


def work_with_db_transact(dbconfig: dict, _SQL1: str, SQL2: str) -> list:
    with UserDatabase(dbconfig) as cursor:
        cursor.execute(_SQL1)
        cursor.execute(SQL2)


def work_with_db_transact_v2(dbconfig: dict, _SQL1: str) -> list:
    connection = connect(**dbconfig)
    with connection.cursor() as cursor:
        connection.begin()
        cursor.execute(_SQL1)
        connection.commit()
        cursor.close()
    connection.close()
