import sqlite3
import threading
from datetime import datetime
import json


class SqliteManager(threading.Thread):
    def __init__(self):
        super().__init__()
        self.create_tables()

    def create_tables(self):
        sql_statements = [ 
            """ CREATE TABLE IF NOT EXISTS suscripciones (
                id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                duration INTEGER,
                entries INTEGER,
                user_id INTEGER
            );"""
        ]

        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                for statement in sql_statements:
                    cursor.execute(statement)
                conn.commit()
        except sqlite3.Error as e:
            print("OCURRIO ALGO")
            print(e)

    def insert_subscription(self, params):
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                
                # Insertar los datos de la suscripción en la tabla
                cursor.execute('''
                    INSERT INTO suscripciones (start_date, end_date, duration, entries, user_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    params['start_date'],
                    params['end_date'],
                    params['duration'],
                    params['entries'],
                    params['user_id']
                ))

                conn.commit()
                print("Suscripción insertada correctamente.")
        except sqlite3.Error as e:
            print("Error al insertar la suscripción:", e)
