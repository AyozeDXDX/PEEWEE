from peewee import MySQLDatabase

# Configuración de la conexión a la BD
# MODIFICAR CREDENCIALES ANTES DE USAR
DB_NAME = 'Empresa'
DB_USER = 'ayoze'
DB_PASS = '9978'
DB_HOST = '127.0.0.1'       # IP de MySQL
DB_PORT = 3306              # Puerto de MySQL

db = MySQLDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

def conectar_bd():
    """
    Intenta conectar a la base de datos "Empresa" utilizando try-except[cite: 17].
    """
    try:
        db.connect()
        print(f"Conexión exitosa a la base de datos '{DB_NAME}'")
        return True
    except Exception as e:
        print(f"Error al conectar a la base de datos '{DB_NAME}': {e}")
        return False

def cerrar_bd():
    """
    Cierra la conexión a la base de datos.
    """
    if not db.is_closed():
        db.close()
        print(f"Conexión a '{DB_NAME}' cerrada.")