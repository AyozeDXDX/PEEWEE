from peewee import *
from conexion import db, conectar_bd, cerrar_bd
from crear_tablas import Cliente, Empleado, Proyecto, EmpleadoProyecto
import datetime
from decimal import Decimal

def insertar_clientes():
    if not conectar_bd():
        return
    
    clientes_para_insertar = [
        Cliente(dni_cif='12345678A', nombre_cliente='Empresa A', tlf='912345678', email='contacto@empresa-a.com'),
        Cliente(dni_cif='B87654321', nombre_cliente='Empresa B', tlf='934567890', email='info@empresa-b.es'),
        Cliente(dni_cif='98765432B', nombre_cliente='Consumidor Final', tlf='600112233', email='cliente@email.com'),
        Cliente(dni_cif='C11111111', nombre_cliente='Empresa Sin Proyectos', tlf='900000000', email='sin.proyectos@empresa.com'),
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
    if not conectar_bd():
        return

    empleados_para_insertar = [
        Empleado(dni='11111111X', nombre='Juan Pérez', jefe=True, email='juan.perez@empresa.com'),
        Empleado(dni='22222222Y', nombre='Ana López', jefe=False, email='ana.lopez@empresa.com'),
        Empleado(dni='33333333Z', nombre='Carlos García', jefe=True, email='carlos.garcia@empresa.com'),
        Empleado(dni='44444444A', nombre='María Rodríguez', jefe=False, email='maria.rodriguez@empresa.com'),
        Empleado(dni='55555555B', nombre='Pedro Sánchez', jefe=True, email='pedro.sanchez@empresa.com'),
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
    if not conectar_bd():
        return

    try:
        with db.atomic():
            cliente_id = '12345678A'
            jefe_proyecto_id = '33333333Z'
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
                fecha_fin='2025-06-30',
                presupuesto=Decimal('15000.00'),
                id_cliente=cliente,
                id_jefe_proyecto=jefe
            )
            print(f"Proyecto '{proyecto.titulo_proyecto}' insertado con ID: {proyecto.id_proyecto}")

    except IntegrityError as e:
        print(f"Error de integridad al insertar el proyecto: {e}")
    except Exception as e:
        print(f"Error inesperado al insertar el proyecto: {e}")
    finally:
        cerrar_bd()

def asignar_empleado_a_proyecto():
    if not conectar_bd():
        return

    try:
        with db.atomic():
            empleado_id = '22222222Y'
            proyecto = Proyecto.get_or_none(Proyecto.titulo_proyecto == 'Desarrollo Web Corporativa')
            empleado = Empleado.get_or_none(Empleado.dni == empleado_id)

            if not empleado:
                print(f"Error: El empleado con DNI '{empleado_id}' no existe.")
                return
            if not proyecto:
                print(f"Error: El proyecto 'Desarrollo Web Corporativa' no existe.")
                return

            EmpleadoProyecto.create(id_empleado=empleado, id_proyecto=proyecto)
            print(f"Empleado '{empleado.nombre}' asignado al proyecto '{proyecto.titulo_proyecto}'.")

    except IntegrityError as e:
        print(f"Error: El empleado {empleado_id} ya está asignado al proyecto. ({e})")
    except Exception as e:
        print(f"Error inesperado al asignar empleado a proyecto: {e}")
    finally:
        cerrar_bd()

def insertar_proyectos_prueba():
    if not conectar_bd():
        return

    try:
        with db.atomic():
            cliente_a = Cliente.get_or_none(Cliente.dni_cif == '12345678A')
            cliente_b = Cliente.get_or_none(Cliente.dni_cif == 'B87654321')
            jefe_juan = Empleado.get_or_none(Empleado.dni == '11111111X')
            jefe_carlos = Empleado.get_or_none(Empleado.dni == '33333333Z')
            jefe_pedro = Empleado.get_or_none(Empleado.dni == '55555555B')

            if not (cliente_a and cliente_b and jefe_juan and jefe_carlos and jefe_pedro):
                print("Error: Faltan clientes o empleados jefe para crear proyectos.")
                return

            p2 = Proyecto.create(
                titulo_proyecto='App Móvil',
                descripcion='Aplicación para iOS y Android',
                fecha_inicio=datetime.date(2024, 3, 1),
                fecha_fin=datetime.date(2025, 12, 31),
                presupuesto=Decimal('25000.00'),
                id_cliente=cliente_b,
                id_jefe_proyecto=jefe_juan
            )

            p3 = Proyecto.create(
                titulo_proyecto='Proyecto Antiguo Barato',
                descripcion='Proyecto terminado hace tiempo',
                fecha_inicio=datetime.date(2019, 1, 1),
                fecha_fin=datetime.date(2020, 6, 30),
                presupuesto=Decimal('5000.00'),
                id_cliente=cliente_a,
                id_jefe_proyecto=jefe_pedro
            )

            ana = Empleado.get_or_none(Empleado.dni == '22222222Y')
            maria = Empleado.get_or_none(Empleado.dni == '44444444A')

            if ana and maria:
                try:
                    proyecto_web = Proyecto.get(Proyecto.titulo_proyecto == 'Desarrollo Web Corporativa')
                    EmpleadoProyecto.create(id_empleado=ana, id_proyecto=proyecto_web)
                except IntegrityError:
                    pass
                try:
                    EmpleadoProyecto.create(id_empleado=maria, id_proyecto=p2)
                except IntegrityError:
                    pass

        print("Proyectos de prueba insertados correctamente.")
    except Exception as e:
        print(f"Error al insertar proyectos de prueba: {e}")
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
    print("\n5. Insertando proyectos de prueba...")
    insertar_proyectos_prueba()
    print("\n--- Proceso de inserción finalizado ---")
