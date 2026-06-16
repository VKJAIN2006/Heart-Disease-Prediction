import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()



def get_connection():
    return mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE")
    )

