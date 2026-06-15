import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()



def get_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

