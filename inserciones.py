from peewee import *
from conexion import db, conectar_bd, cerrar_bd
from crear_tablas import Cliente, Empleado, Proyecto, EmpleadoProyecto

def insertar_clientes():
    """
    Inserta múltiples clientes en la tabla 'clientes' utilizando bulk_create()
    definiendo los datos como una lista de objetos Cliente.
    """
    if not conectar_bd():
        return
    
    # creamos una lista de objetos Cliente
    clientes_para_insertar = [
        Cliente(dni_cif='12345678A', nombre_cliente='Empresa A', tlf='912345678', email='contacto@empresa-a.com'),
        Cliente(dni_cif='B87654321', nombre_cliente='Empresa B', tlf='934567890', email='info@empresa-b.es'),
        Cliente(dni_cif='98765432B', nombre_cliente='Consumidor Final', tlf='600112233', email='cliente@email.com'),
    ]

    try:
        with db.atomic():
            Cliente.bulk_create(clientes_para_insertar)
        
        print(f"{len(clientes_para_insertar)} clientes insertados correctamente.")
    except IntegrityError as e:
        print(f"Error de integridad al insertar clientes: {e}")
    except Exception as e:
        print(f"Error inesperado al insertar clientes: {e}")
    finally:
        cerrar_bd()

def insertar_empleados():
    """
    Inserta múltiples empleados en la tabla 'empleados' utilizando bulk_create()
    definiendo los datos como una lista de objetos Empleado.
    """
    if not conectar_bd():
        return

    # Definimos los datos como una lista de objetos Empleado
    empleados_para_insertar = [
        Empleado(dni='11111111X', nombre='Juan Pérez', jefe=True, email='juan.perez@empresa.com'),
        Empleado(dni='22222222Y', nombre='Ana López', jefe=False, email='ana.lopez@empresa.com'),
        Empleado(dni='33333333Z', nombre='Carlos García', jefe=False, email='carlos.garcia@empresa.com'),
    ]

    try:
        with db.atomic():
            Empleado.bulk_create(empleados_para_insertar)

        print(f"{len(empleados_para_insertar)} empleados insertados correctamente.")
    except IntegrityError as e:
        print(f"Error de integridad al insertar empleados: {e}")
    except Exception as e:
        print(f"Error inesperado al insertar empleados: {e}")
    finally:
        cerrar_bd()

def insertar_proyecto():
    """
    Inserta un proyecto en la tabla 'proyectos' utilizando create().
    Verifica la existencia del cliente y del jefe de proyecto.
    """
    if not conectar_bd():
        return

    try:
        with db.atomic():
            # IDs del cliente y jefe de proyecto que deben existir
            cliente_id = '12345678A'
            jefe_proyecto_id = '11111111X'

            # Verificar que el cliente y el empleado existen
            cliente = Cliente.get_or_none(Cliente.dni_cif == cliente_id)
            jefe = Empleado.get_or_none((Empleado.dni == jefe_proyecto_id) & (Empleado.jefe == True))

            if not cliente:
                print(f"Error: El cliente con DNI/CIF '{cliente_id}' no existe.")
                return
            if not jefe:
                print(f"Error: El empleado con DNI '{jefe_proyecto_id}' no existe o no es jefe.")
                return

            proyecto = Proyecto.create(
                titulo_proyecto='Desarrollo Web Corporativa',
                descripcion='Creación de la página web y tienda online para Empresa A.',
                fecha_inicio='2024-01-15',
                presupuesto=15000.00,
                id_cliente=cliente,  # Pasamos el objeto Cliente
                id_jefe_proyecto=jefe # Pasamos el objeto Empleado
            )
            print(f"Proyecto '{proyecto.titulo_proyecto}' insertado con ID: {proyecto.id_proyecto}")

    except IntegrityError as e:
        print(f"Error de integridad al insertar el proyecto: {e}")
    except Exception as e:
        print(f"Error inesperado al insertar el proyecto: {e}")
    finally:
        cerrar_bd()

def asignar_empleado_a_proyecto():
    """
    Asigna un empleado a un proyecto en la tabla 'empleados_proyecto' utilizando create().
    """
    if not conectar_bd():
        return

    try:
        with db.atomic():
            empleado_id = '22222222Y'
            proyecto_id = 1

            # Verificar que el empleado y el proyecto existen
            empleado = Empleado.get_or_none(Empleado.dni == empleado_id)
            proyecto = Proyecto.get_or_none(Proyecto.id_proyecto == proyecto_id)

            if not empleado:
                print(f"Error: El empleado con DNI '{empleado_id}' no existe.")
                return
            if not proyecto:
                print(f"Error: El proyecto con ID '{proyecto_id}' no existe.")
                return

            # Asignar el empleado al proyecto
            EmpleadoProyecto.create(
                id_empleado=empleado,
                id_proyecto=proyecto
            )
            print(f"Empleado '{empleado.nombre}' asignado al proyecto '{proyecto.titulo_proyecto}'.")

    except IntegrityError as e:
        # Esto puede ocurrir si la asignación ya existe (clave primaria compuesta)
        print(f"Error: El empleado {empleado_id} ya está asignado al proyecto {proyecto_id}. ({e})")
    except Exception as e:
        print(f"Error inesperado al asignar empleado a proyecto: {e}")
    finally:
        cerrar_bd()

if __name__ == '__main__':
    print("--- Ejecutando inserciones ---")
    
    print("\n1. Insertando clientes...")
    insertar_clientes()
    
    print("\n2. Insertando empleados...")
    insertar_empleados()

    print("\n3. Insertando un proyecto...")
    insertar_proyecto()

    print("\n4. Asignando un empleado a un proyecto...")
    asignar_empleado_a_proyecto()

    print("\n--- Proceso de inserción finalizado ---")