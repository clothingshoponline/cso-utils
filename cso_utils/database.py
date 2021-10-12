import pymysql.cursors
import platform
import os


class Database:
    '''
    Used to create a database connection on either Windows or Linux operating systems (Java not supported)
    This has been tested to work with Google Cloud SQL but it should work with other databases as well.

    Example: sql = Database(username, password, db_name, port_or_socket)

    Parameters:
    username -- Database username
    password -- Database password
    db_name -- Database name
    port_or_socket -- Use port if running on Windows, use socket if running on Linux.
    '''

    def __init__(self, username: str, password: str, db_name: str, port_or_socket: str):
        os_type = platform.system()
        if os_type == "Windows":
            connection = pymysql.connect(
                host='127.0.0.1',
                port=int(port_or_socket),
                user=username,
                password=password,
                database=db_name,
                autocommit=True,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        elif os_type == "Linux":
            connection = pymysql.connect(
                unix_socket=port_or_socket,
                user=username,
                password=password,
                database=db_name,
                autocommit=True,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        # self.connection = connection
        self.cursor = connection.cursor()

    def get_table_names(self) -> list:
        '''
        Lists the non-TEMPORARY tables in a given database.
        '''
        cursor = self.cursor
        cursor.execute(
            '''
            SHOW TABLES
            '''
        )
        return cursor.fetchall()

    def get_table_schema(self, table_name) -> list:
        '''
        Provides information about columns in the given table.
        '''
        cursor = self.cursor
        cursor.execute(
            f'''
            SELECT *
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_name = '{table_name}'
            '''
        )
        return cursor.fetchall()
