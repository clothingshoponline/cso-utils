import pymysql.cursors
import platform
import os


def connection(username, password, db_name, port_or_socket):
    '''
    This can be used to connect to a database, regardless of the clients operating system.
    This has been tested to work with Google Cloud SQL but it should work with other databases as well.

    Parameters:
    username -- Database username
    password -- Database password
    db_name -- Database name
    port_or_socket -- Use port if running on Windows, use socket if running on Linux
    '''
    operating_system = platform.system()
    if operating_system == "Windows":
        connection = pymysql.connect(
            host='127.0.0.1',
            port=port_or_socket,
            user=username,
            passwd=password,
            db=db_name,
            autocommit=True,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection.cursor()
    elif operating_system == "Linux":
        connection = pymysql.connect(
            unix_socket=port_or_socket,
            user=username,
            passwd=password,
            db=db_name,
            autocommit=True,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection.cursor()
    else:
        return {"Error": "Cound not determine the operating system type."}
