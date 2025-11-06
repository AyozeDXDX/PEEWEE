from peewee import *
# Importa la conexión definida en el archivo anterior [cite: 19]
from conexion import db, conectar_bd, cerrar_bd 
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

# --- Clase Base para los Modelos ---
class BaseModel(Model):
    class Meta:
        database = db

# --- 1. Modelos Principales (Entidades) ---

# Clientes: DNI / CIF (PK alfanumérico), nombre_cliente, tlf, email [cite: 8]
class Cliente(BaseModel):
    # DNI o CIF debe ser la PK de tipo alfanumérico [cite: 8]
    dni_cif = CharField(max_length=15, primary_key=True, column_name='dni_cif')
    nombre_cliente = CharField(max_length=100)
    tlf = CharField(max_length=15, null=True)
    email = CharField(max_length=100, unique=True)

    class Meta:
        table_name = 'clientes'

# Empleados: DNI (PK alfanumérico), nombre, jefe (booleano), email [cite: 9, 10]
class Empleado(BaseModel):
    # DNI PK alfanumérico [cite: 9]
    dni = CharField(max_length=15, primary_key=True, column_name='dni')
    nombre = CharField(max_length=100)
    # Campo "Jefe" de tipo booleano [cite: 10]
    jefe = BooleanField(default=False) 
    email = CharField(max_length=100, unique=True)

    class Meta:
        table_name = 'empleados'

# Proyectos [cite: 11]
class Proyecto(BaseModel):
    # id_proyecto (PK autoincremental) [cite: 11]
    id_proyecto = AutoField(column_name='id_proyecto')
    titulo_proyecto = CharField(max_length=255)
    descripcion = TextField(null=True)
    fecha_inicio = DateField()
    fecha_fin = DateField(null=True)
    presupuesto = DecimalField(max_digits=10, decimal_places=2)

    # FK a Clientes (1:N) - Un cliente puede solicitar varios proyectos [cite: 5, 11]
    # Se usa column_name explícitamente 
    id_cliente = ForeignKeyField(
        Cliente, 
        field=Cliente.dni_cif, # La columna dni_cif de Cliente es la PK
        backref='proyectos', 
        column_name='id_cliente'
    )

    # FK a Empleados (1:1) - Cada proyecto tiene un único jefe [cite: 7, 11]
    # unique=True garantiza que este DNI de empleado solo aparezca una vez como jefe, 
    # implementando "Un jefe sólo puede serlo de un proyecto"[cite: 14].
    # Se usa column_name explícitamente 
    id_jefe_proyecto = ForeignKeyField(
        Empleado, 
        field=Empleado.dni, 
        backref='proyectos_dirigidos', 
        column_name='id_jefe_proyecto',
        unique=True 
    ) 

    class Meta:
        table_name = 'proyectos'


# --- 2. Modelo de Intersección (Relación M:N) ---

# Empleados-Proyecto: Tabla de la relación M:N [cite: 6, 11]
class EmpleadoProyecto(BaseModel):
    # FK a Empleado (M:N) [cite: 6]
    # Se usa column_name explícitamente 
    id_empleado = ForeignKeyField(
        Empleado, 
        field=Empleado.dni, 
        backref='participaciones', 
        column_name='id_empleado'
    )

    # FK a Proyecto (M:N) [cite: 6]
    # Se usa column_name explícitamente 
    id_proyecto = ForeignKeyField(
        Proyecto, 
        field=Proyecto.id_proyecto, 
        backref='asignaciones', 
        column_name='id_proyecto'
    )

    class Meta:
        table_name = 'empleados_proyecto'
        # CORRECCIÓN: Se usan cadenas de texto para definir la clave primaria compuesta
        # Esto resuelve el error de "variable no definida"
        primary_key = CompositeKey('id_empleado', 'id_proyecto') 


# --- Función para crear las tablas ---
def crear_tablas():
    """
    Crea las tablas de la base de datos si no existen.
    """
    # El orden es importante para las FKs (no crear Proyecto antes que Cliente/Empleado)
    modelos = [Cliente, Empleado, Proyecto, EmpleadoProyecto] 
    
    if conectar_bd():
        try:
            # Drop tables for clean start (opcional, comentar si no se quiere borrar datos)
            # db.drop_tables(modelos) 
            
            db.create_tables(modelos)
            logger.info("Modelos de datos y tablas creadas exitosamente.")
        except Exception as e:
            logger.error(f"Error al crear las tablas: {e}")
        finally:
            cerrar_bd()
    else:
        logger.error("No se pudo establecer la conexión para crear las tablas.")


if __name__ == '__main__':
    # Ejecutar la creación de tablas
    crear_tablas()