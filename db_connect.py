import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # thay bằng user MySQL của bạn
        password="248569",    # thay bằng password MySQL của bạn
        database="qlxemay"
    )