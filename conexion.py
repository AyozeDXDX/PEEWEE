from peewee import MySQLDatabase
import logging

# Configuración de la conexión a la BD
# *** MODIFICA ESTOS VALORES CON TUS CREDENCIALES ***
DB_NAME = 'Empresa'
DB_USER = 'tu_usuario'      # Ejemplo: 'root'
DB_PASS = 'tu_contraseña'   # Ejemplo: 'password'
DB_HOST = 'localhost'       # O la IP de tu servidor MySQL
DB_PORT = 3306              # Puerto estándar de MySQL

# Inicializar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancia de la base de datos (Global)
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
        logger.info(f"Conexión exitosa a la base de datos '{DB_NAME}'")
        return True
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos '{DB_NAME}': {e}")
        return False

def cerrar_bd():
    """
    Cierra la conexión a la base de datos.
    """
    if not db.is_closed():
        db.close()
        logger.info(f"Conexión a '{DB_NAME}' cerrada.")

if __name__ == '__main__':
    if conectar_bd():
        # Aquí se podría poner código de prueba de conexión
        pass
    cerrar_bd()