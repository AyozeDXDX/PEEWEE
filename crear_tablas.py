from peewee import *
from conexion import db, conectar_bd, cerrar_bd

# --- Clase Base para los Modelos ---
class BaseModel(Model):
    class Meta:
        database = db
# Clientes: DNI / CIF (PK varchar), nombre_cliente, tlf, email
class Cliente(BaseModel):
    dni_cif = CharField(max_length=15, primary_key=True, column_name='dni_cif')
    nombre_cliente = CharField(max_length=100)
    tlf = CharField(max_length=15, null=True)
    email = CharField(max_length=100, unique=True)

    class Meta:
        table_name = 'clientes'

# Empleados: DNI (PK varchar), nombre, jefe (booleano), email
class Empleado(BaseModel):
    dni = CharField(max_length=15, primary_key=True, column_name='dni')
    nombre = CharField(max_length=100)
    jefe = BooleanField(default=False) 
    email = CharField(max_length=100, unique=True)

    class Meta:
        table_name = 'empleados'

# Proyectos
class Proyecto(BaseModel):
    # id_proyecto (autoincremental)
    id_proyecto = AutoField(column_name='id_proyecto')
    titulo_proyecto = CharField(max_length=255)
    descripcion = TextField(null=True)
    fecha_inicio = DateField()
    fecha_fin = DateField(null=True)
    presupuesto = DecimalField(max_digits=10, decimal_places=2)

    # FK a Clientes (1:N) - Un cliente puede solicitar varios proyectos
    id_cliente = ForeignKeyField(
        Cliente, 
        field=Cliente.dni_cif, # La columna dni_cif de Cliente es la PK
        backref='proyectos', 
        column_name='id_cliente'
    )

    # FK a Empleados (1:1) - Un proyecto tiene un único jefe de proyecto
    id_jefe_proyecto = ForeignKeyField(
        Empleado, 
        field=Empleado.dni, 
        backref='proyectos_dirigidos', 
        column_name='id_jefe_proyecto',
        unique=True 
    ) 

    class Meta:
        table_name = 'proyectos'

# Empleados-Proyecto: Tabla de la relación M:N
class EmpleadoProyecto(BaseModel):
    # FK Empleado (M:N)
    id_empleado = ForeignKeyField(
        Empleado, 
        field=Empleado.dni, 
        backref='participaciones', 
        column_name='id_empleado'
    )

    # FK Proyecto (M:N)
    id_proyecto = ForeignKeyField(
        Proyecto, 
        field=Proyecto.id_proyecto, 
        backref='asignaciones', 
        column_name='id_proyecto'
    )

    class Meta:
        table_name = 'empleados_proyecto'
        primary_key = CompositeKey('id_empleado', 'id_proyecto') 


# --- Función para crear las tablas ---
def crear_tablas():
    """
    Crea las tablas de la base de datos si no existen.
    """
    modelos = [Cliente, Empleado, Proyecto, EmpleadoProyecto] 
    
    if conectar_bd():
        try:
            db.create_tables(modelos)
            print("Modelos de datos y tablas creadas exitosamente.")
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
        finally:
            cerrar_bd()
    else:
        print("No se pudo establecer la conexión para crear las tablas.")

if __name__ == '__main__':
    # Ejecutar la creación de tablas
    crear_tablas()