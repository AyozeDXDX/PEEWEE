# main_actividades.py

import datetime
from peewee import *
# Importamos la conexión y los modelos de los archivos proporcionados
from conexion import db, conectar_bd, cerrar_bd
from crear_tablas import Cliente, Empleado, Proyecto, EmpleadoProyecto

# --- 1. Actualizar Teléfono de Cliente (.save()) ---
def actualizar_telefono_cliente(dni_cif, nuevo_telefono):
    """
    Actualiza el número de teléfono de un cliente específico
    utilizando el método .save().
    """
    if not conectar_bd():
        return

    try:
        # 1. Encontrar al cliente
        cliente = Cliente.get_or_none(Cliente.dni_cif == dni_cif)

        if cliente:
            # 2. Modificar el atributo
            cliente.tlf = nuevo_telefono
            
            # 3. Guardar los cambios en la BD
            cliente.save() 
            print(f"Teléfono del cliente '{cliente.nombre_cliente}' actualizado a {nuevo_telefono}.")
        else:
            print(f"Error: No se encontró ningún cliente con DNI/CIF {dni_cif}.")

    except Exception as e:
        print(f"Error al actualizar el teléfono del cliente: {e}")
    finally:
        cerrar_bd()

# --- 2. Aumentar Presupuesto Proyectos Activos (.update()) ---
def aumentar_presupuesto_proyectos_activos():
    """
    Aumenta el presupuesto de todos los proyectos activos en un 10%.
    Un proyecto se considera activo si su fecha_fin es futura o es NULA.
    Utiliza una expresión aritmética en .update().
    """
    if not conectar_bd():
        return

    try:
        fecha_actual = datetime.date.today()

        # Condición: proyectos cuya fecha de finalización sea posterior a hoy,
        # O proyectos que no tengan fecha de finalización (NULL)
        condicion_activos = (Proyecto.fecha_fin > fecha_actual) | (Proyecto.fecha_fin.is_null(True))

        # Expresión aritmética para el aumento (presupuesto * 1.10)
        expresion_aumento = Proyecto.presupuesto * 1.10

        # Construir la consulta de actualización
        query = Proyecto.update(presupuesto=expresion_aumento).where(condicion_activos)
        
        # Ejecutar la consulta
        filas_actualizadas = query.execute()
        
        print(f"Se aumentó el presupuesto en un 10% a {filas_actualizadas} proyectos activos.")

    except Exception as e:
        print(f"Error al aumentar el presupuesto de los proyectos: {e}")
    finally:
        cerrar_bd()

# --- 3. Reasignar Jefe de Proyecto (.save()) ---
def reasignar_jefe_proyecto(id_proyecto, nuevo_jefe_dni):
    """
    Reasigna el jefe de proyecto para un proyecto específico.
    Utiliza .save() para actualizar el registro existente.
    """
    if not conectar_bd():
        return

    try:
        # 1. Buscar el proyecto
        proyecto = Proyecto.get_or_none(Proyecto.id_proyecto == id_proyecto)
        
        # 2. Buscar al nuevo empleado (y asegurarse de que sea jefe)
        nuevo_jefe = Empleado.get_or_none(
            (Empleado.dni == nuevo_jefe_dni) & (Empleado.jefe == True)
        )

        if not proyecto:
            print(f"Error: No se encontró el proyecto con ID {id_proyecto}.")
            return
        
        if not nuevo_jefe:
            print(f"Error: No se encontró al empleado {nuevo_jefe_dni} o no es jefe.")
            return

        # 3. Reasignar la clave foránea (FK)
        proyecto.id_jefe_proyecto = nuevo_jefe
        
        # 4. Guardar el cambio.
        # Peewee sabe que es un UPDATE porque 'proyecto' se obtuvo de la BD.
        # save() por defecto NO crea un nuevo registro si el objeto ya existe.
        proyecto.save() 
        
        print(f"El proyecto '{proyecto.titulo_proyecto}' ha sido reasignado a '{nuevo_jefe.nombre}'.")

    except IntegrityError:
        # Esto saltaría si el jefe ya dirige otro proyecto (ya que la FK es unique=True)
        print(f"Error de integridad: El empleado '{nuevo_jefe.nombre}' ya es jefe de otro proyecto.")
    except Exception as e:
        print(f"Error al reasignar el jefe de proyecto: {e}")
    finally:
        cerrar_bd()

# --- 4. Eliminar Clientes sin Proyectos (Subconsulta) ---
def eliminar_clientes_sin_proyectos():
    """
    Elimina los clientes que no tengan ningún proyecto asociado,
    utilizando delete() y una subconsulta.
    """
    if not conectar_bd():
        return

    try:
        # 1. Subconsulta: Obtener los DNI/CIF de todos los clientes 
        # que SÍ están en la tabla de Proyectos.
        subconsulta_clientes_con_proyectos = Proyecto.select(Proyecto.id_cliente).distinct()

        # 2. Consulta Delete: Borrar de Cliente
        # donde el dni_cif NO ESTÉ EN la subconsulta.
        query = Cliente.delete().where(
            Cliente.dni_cif.not_in(subconsulta_clientes_con_proyectos)
        )

        filas_eliminadas = query.execute()

        print(f"Se eliminaron {filas_eliminadas} clientes que no tenían proyectos asociados.")

    except Exception as e:
        print(f"Error al eliminar clientes sin proyectos: {e}")
    finally:
        cerrar_bd()

# --- 5. Borrar Proyectos Antiguos y Baratos (where()) ---
def eliminar_proyectos_antiguos_baratos():
    """
    Elimina proyectos cuyo presupuesto sea < 10,000 Y
    cuya fecha de finalización ya haya pasado.
    Utiliza delete() y una consulta condicional where().
    """
    if not conectar_bd():
        return
        
    try:
        fecha_actual = datetime.date.today()

        # 1. Definir la condición con 'Y' (&)
        condicion = (Proyecto.presupuesto < 10000) & (Proyecto.fecha_fin < fecha_actual)

        # 2. Construir la consulta de borrado
        query = Proyecto.delete().where(condicion) 

        filas_eliminadas = query.execute()
        
        print(f"Se eliminaron {filas_eliminadas} proyectos antiguos y con bajo presupuesto.")

    except Exception as e:
        print(f"Error al eliminar los proyectos: {e}")
    finally:
        cerrar_bd()

# --- 6. Transacción: Limpieza Proyectos Antiguos (5 años) ---
def transaccion_limpieza_proyectos(id_proyecto_destino):
    """
    Realiza una transacción para:
    1. Reasignar empleados de proyectos obsoletos (terminados hace >5 años) 
       a un nuevo proyecto activo.
    2. Eliminar esos proyectos obsoletos.
    """
    if not conectar_bd():
        return

    try:
        # 1. Verificar que el proyecto destino existe
        proyecto_destino = Proyecto.get_or_none(Proyecto.id_proyecto == id_proyecto_destino)
        if not proyecto_destino:
            print(f"Error: El proyecto destino con ID {id_proyecto_destino} no existe.")
            return

        # 2. Calcular la fecha límite (hace 5 años)
        # Usamos SQL para el cálculo de 5 años
        fecha_limite = fn.NOW() - SQL('INTERVAL 5 YEAR')

        # 3. Subconsulta: Obtener los IDs de los proyectos obsoletos
        subconsulta_proyectos_obsoletos = Proyecto.select(Proyecto.id_proyecto).where(
            (Proyecto.fecha_fin < fecha_limite) & (Proyecto.fecha_fin.is_null(False))
        )

        # 4. Iniciar la transacción
        with db.atomic():
            print("Iniciando transacción...")
            
            # --- Paso 1: Actualizar asignaciones de empleados ---
            # Busca en EmpleadoProyecto las asignaciones a proyectos obsoletos
            # y les asigna el nuevo id_proyecto_destino.
            query_update = EmpleadoProyecto.update(
                id_proyecto=proyecto_destino
            ).where(
                EmpleadoProyecto.id_proyecto.in_(subconsulta_proyectos_obsoletos)
            )
            empleados_reasignados = query_update.execute()
            print(f"[Transacción] {empleados_reasignados} asignaciones de empleados actualizadas.")

            # --- Paso 2: Eliminar los proyectos obsoletos ---
            query_delete = Proyecto.delete().where(
                Proyecto.id_proyecto.in_(subconsulta_proyectos_obsoletos)
            )
            proyectos_eliminados = query_delete.execute()
            print(f"[Transacción] {proyectos_eliminados} proyectos obsoletos eliminados.")

        print("Transacción completada exitosamente.")

    except IntegrityError as e:
        # Esto podría pasar si un empleado reasignado ya estaba en el proyecto destino
        print(f"Error de integridad en la transacción (posible duplicado de empleado). Rollback realizado. {e}")
    except Exception as e:
        print(f"Error durante la transacción. Rollback realizado. {e}")
    finally:
        cerrar_bd()

# --- 7. Eliminar Cliente y Datos Asociados (Cascada Manual) ---
def eliminar_cliente_y_proyectos(dni_cif):
    """
    Elimina un cliente y todos sus datos asociados, incluidos 
    los proyectos que tuviera encargados.
    (Requiere borrado manual en cascada si no está en la BD).
    """
    if not conectar_bd():
        return

    try:
        # 1. Buscar al cliente
        cliente_a_borrar = Cliente.get_or_none(Cliente.dni_cif == dni_cif)
        
        if not cliente_a_borrar:
            print(f"Error: No se encontró al cliente {dni_cif}.")
            return
        
        print(f"Iniciando borrado en cascada para el cliente: {cliente_a_borrar.nombre_cliente}...")

        # 2. Iniciar transacción para asegurar que todo se borre o nada se borre
        with db.atomic():
            
            # 3. Subconsulta: Obtener los IDs de los proyectos de ESE cliente
            proyectos_del_cliente = Proyecto.select(Proyecto.id_proyecto).where(
                Proyecto.id_cliente == cliente_a_borrar
            )

            # 4. Borrar asignaciones (EmpleadoProyecto) de esos proyectos
            # (Hay que borrar esto primero por la FK de EmpleadoProyecto -> Proyecto)
            q_delete_asig = EmpleadoProyecto.delete().where(
                EmpleadoProyecto.id_proyecto.in_(proyectos_del_cliente)
            )
            asignaciones_borradas = q_delete_asig.execute()
            print(f"[Transacción] {asignaciones_borradas} asignaciones de empleados eliminadas.")

            # 5. Borrar los Proyectos de ese cliente
            # (Hay que borrar esto antes que el Cliente por la FK de Proyecto -> Cliente)
            q_delete_proy = Proyecto.delete().where(
                Proyecto.id_cliente == cliente_a_borrar
            )
            proyectos_borrados = q_delete_proy.execute()
            print(f"[Transacción] {proyectos_borrados} proyectos eliminados.")

            # 6. Finalmente, borrar el Cliente
            # cliente_a_borrar.delete_instance() # También es válido
            q_delete_cli = Cliente.delete().where(
                Cliente.dni_cif == cliente_a_borrar.dni_cif
            )
            clientes_borrados = q_delete_cli.execute()
            print(f"[Transacción] {clientes_borrados} cliente eliminado.")
        
        print(f"Cliente {dni_cif} y todos sus datos asociados fueron eliminados.")

    except IntegrityError as e:
        print(f"Error de integridad. No se pudieron borrar todos los datos. Rollback realizado. {e}")
    except Exception as e:
        print(f"Error al eliminar el cliente y sus datos. Rollback realizado. {e}")
    finally:
        cerrar_bd()


# --- Bloque Principal de Ejecución (Ejemplos) ---
if __name__ == '__main__':
    
    print("--- Ejecutando Operaciones de Actualización y Borrado ---")

    # (Asegúrate de tener datos insertados primero ejecutando inserciones.py)
    
    # --- Ejemplo 1: Actualizar teléfono ---
    # print("\n--- 1. Actualizando teléfono de 'Empresa A' ---")
    # actualizar_telefono_cliente(dni_cif='12345678A', nuevo_telefono='911111111')

    # --- Ejemplo 2: Aumentar presupuestos ---
    # (Necesitarías insertar proyectos activos/inactivos para probar esto)
    # print("\n--- 2. Aumentando presupuestos 10% ---")
    # aumentar_presupuesto_proyectos_activos()

    # --- Ejemplo 3: Reasignar jefe ---
    # (Suponiendo que el proyecto 1 existe y el empleado '33333333Z' existe)
    # (Para que funcione, 'Carlos García' (33333333Z) debería ser jefe=True)
    # print("\n--- 3. Reasignando jefe del proyecto 1 ---")
    # reasignar_jefe_proyecto(id_proyecto=1, nuevo_jefe_dni='33333333Z')

    # --- Ejemplo 4: Eliminar clientes sin proyectos ---
    # (Insertar un cliente nuevo sin proyecto para probar)
    # print("\n--- 4. Eliminando clientes sin proyectos ---")
    # eliminar_clientes_sin_proyectos()

    # --- Ejemplo 5: Eliminar proyectos antiguos/baratos ---
    # (Necesitarías insertar un proyecto con presupuesto=5000 y fecha_fin='2020-01-01')
    # print("\n--- 5. Eliminando proyectos antiguos y baratos ---")
    # eliminar_proyectos_antiguos_baratos()

    # --- Ejemplo 6: Transacción de limpieza ---
    # (Esta es compleja de probar. Necesitas un proyecto terminado hace > 5 años
    # y un proyecto destino (p.ej. ID 1) para mover los empleados)
    # print("\n--- 6. Ejecutando transacción de limpieza (5 años) ---")
    # transaccion_limpieza_proyectos(id_proyecto_destino=1)

    # --- Ejemplo 7: Eliminar cliente y cascada ---
    # (Esto eliminará a 'Empresa B' y sus proyectos (si tuviera))
    # print("\n--- 7. Eliminando cliente 'Empresa B' y sus datos ---")
    # eliminar_cliente_y_proyectos(dni_cif='B87654321')

    print("\n--- Operaciones finalizadas ---")