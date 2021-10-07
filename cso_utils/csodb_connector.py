import pymysql.cursors
import platform
import os


def connection(windows_port=40000):
    '''
    This function creates a connection to the Google Cloud SQL "main" database.
    It uses the platform library to determine if the connection is for Windows or Linux
    '''
    if platform.system() == "Windows":
        connection = pymysql.connect(
            host='127.0.0.1',
            port=windows_port,  # make sure this port number matches the port number in the command used to start the proxy
            user=os.getenv("GCP_SQL_USER"),
            passwd=os.getenv("GCP_SQL_PASS"),
            db=os.getenv("GCP_SQL_DBNAME"),
            autocommit=True,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection.cursor()
    elif platform.system() == "Linux":
        connection = pymysql.connect(
            unix_socket=os.getenv("GCP_SQL_CONNECTION_NAME"),
            user=os.getenv("GCP_SQL_USER"),
            passwd=os.getenv("GCP_SQL_PASS"),
            db=os.getenv("GCP_SQL_DBNAME"),
            autocommit=True,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection.cursor()
    else:
        return {"Error": "Cound not determine platform type."}
