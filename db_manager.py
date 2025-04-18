import sqlite3



class SqliteManager():
    def __init__(self):
        super().__init__()
        self.create_tables()

    def create_tables(self):
        sql_statements = [ 
            """ CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                duration INTEGER,
                entries INTEGER,
                user_id INTEGER
            );
            """,
            """ CREATE TABLE IF NOT EXISTS staff_members  (
                id INTEGER PRIMARY KEY,
                admin_id INTEGER,
                name TEXT,
                lastname TEXT,
                email TEXT,
                account_type TEXT
            );
            """
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
                    INSERT INTO subscriptions (start_date, end_date, duration, entries, user_id)
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
    def insert_admin(self, params):
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO staff_members (admin_id, name, lastname, email,account_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    params['admin_id'],
                    params['name'],
                    params['lastname'],
                    params['email'],
                    params['account_type']
                ))

                conn.commit()
                print("Admin insertado correctamente.")
        except sqlite3.Error as e:
            print("Error al insertar la administracion", e)

    def get_subscription_by_user_id(self, user_id):
        """Busca en la tabla subscriptions la fila que coincida con el user_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM subscriptions WHERE user_id = ?
                ''', (user_id,))
                
                subscription = cursor.fetchone()  # Obtener la primera coincidencia

                if subscription:
                    # # Convertir la tupla en un diccionario para una mejor presentación
                    subscription_dict = {
                        "id": subscription[0],
                        "start_date": subscription[1],
                        "end_date": subscription[2],
                        "duration": subscription[3],
                        "entries": subscription[4],
                        "user_id": subscription[5]
                    }
                    return subscription_dict
                else:
                    return None  # No se encontró suscripción para ese user_id

        except sqlite3.Error as e:
            print("Error al buscar la suscripción:", e)
            return False
    def get_admin_by_id(self, admin_id):
        """Busca en la tabla admin la fila que coincida con el admin_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM staff_members WHERE admin_id = ?
                ''', (admin_id,))
                admin_data = cursor.fetchone()  # Obtener la primera coincidencia
                if admin_data:
                    return True
                else:
                    return False

        except sqlite3.Error as e:
            print("Error al buscar la suscripción:", e)
            return False
    def update_subscription_dates(self, subscription_id, new_start_date, new_end_date):
        """Actualiza start_date y end_date en la suscripción con el ID proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE subscriptions 
                    SET start_date = ?, end_date = ? 
                    WHERE id = ?
                ''', (new_start_date, new_end_date, subscription_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Suscripción {subscription_id} actualizada correctamente.")
                    return True
                else:
                    print(f"No se encontró la suscripción con ID {subscription_id}.")
                    return False

        except sqlite3.Error as e:
            print("Error al actualizar la suscripción:", e)
            return False

