# main_actividades.py

import datetime
from peewee import *
from conexion import db, conectar_bd, cerrar_bd
from crear_tablas import Cliente, Empleado, Proyecto, EmpleadoProyecto

# --- 1. Actualizar Teléfono de Cliente ---
def actualizar_telefono_cliente(dni_cif, nuevo_telefono):
    """
    Actualiza el número de teléfono de un cliente específico
    utilizando el método .save().
    """
    if not conectar_bd():
        return

    try:
        cliente = Cliente.get_or_none(Cliente.dni_cif == dni_cif)

        if cliente:
            cliente.tlf = nuevo_telefono
            cliente.save() 
            print(f"Teléfono del cliente '{cliente.nombre_cliente}' actualizado a {nuevo_telefono}.")
        else:
            print(f"Error: No se encontró ningún cliente con DNI/CIF {dni_cif}.")

    except Exception as e:
        print(f"Error al actualizar el teléfono del cliente: {e}")
    finally:
        cerrar_bd()

# --- 2. Aumentar Presupuesto Proyectos Activos ---
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

        # Proyectos activos: fecha_fin futura O NULL
        fecha_fin_futura = Proyecto.fecha_fin > fecha_actual
        fecha_fin_nula = Proyecto.fecha_fin.is_null(True)
        condicion_activos = fecha_fin_futura | fecha_fin_nula
        
        expresion_aumento = Proyecto.presupuesto * 1.10
        query = Proyecto.update(presupuesto=expresion_aumento).where(condicion_activos)
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
        proyecto = Proyecto.get_or_none(Proyecto.id_proyecto == id_proyecto)
        
        es_jefe = Empleado.jefe == True
        es_mismo_dni = Empleado.dni == nuevo_jefe_dni
        nuevo_jefe = Empleado.get_or_none(es_mismo_dni & es_jefe)

        if not proyecto:
            print(f"Error: No se encontró el proyecto con ID {id_proyecto}.")
            return
        
        if not nuevo_jefe:
            print(f"Error: No se encontró al empleado {nuevo_jefe_dni} o no es jefe.")
            return

        proyecto.id_jefe_proyecto = nuevo_jefe
        proyecto.save() 
        
        print(f"El proyecto '{proyecto.titulo_proyecto}' ha sido reasignado a '{nuevo_jefe.nombre}'.")

    except IntegrityError:
        print(f"Error de integridad: El empleado '{nuevo_jefe.nombre}' ya es jefe de otro proyecto.")
    except Exception as e:
        print(f"Error al reasignar el jefe de proyecto: {e}")
    finally:
        cerrar_bd()

# --- 4. Eliminar Clientes sin Proyectos ---
def eliminar_clientes_sin_proyectos():
    """
    Elimina los clientes que no tengan ningún proyecto asociado,
    utilizando delete() y una subconsulta.
    """
    if not conectar_bd():
        return

    try:
        subconsulta_clientes_con_proyectos = Proyecto.select(Proyecto.id_cliente).distinct()

        query = Cliente.delete().where(
            Cliente.dni_cif.not_in(subconsulta_clientes_con_proyectos)
        )

        filas_eliminadas = query.execute()

        print(f"Se eliminaron {filas_eliminadas} clientes que no tenían proyectos asociados.")

    except Exception as e:
        print(f"Error al eliminar clientes sin proyectos: {e}")
    finally:
        cerrar_bd()

# --- 5. Borrar Proyectos Antiguos y Baratos ---
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

        presupuesto_bajo = Proyecto.presupuesto < 10000
        fecha_pasada = Proyecto.fecha_fin < fecha_actual
        condicion = presupuesto_bajo & fecha_pasada
        
        query = Proyecto.delete().where(condicion) 
        filas_eliminadas = query.execute()
        
        print(f"Se eliminaron {filas_eliminadas} proyectos antiguos y con bajo presupuesto.")

    except Exception as e:
        print(f"Error al eliminar los proyectos: {e}")
    finally:
        cerrar_bd()

# --- 6. Transacción: Limpieza Proyectos Antiguos ---
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

        # 2. Calcular la fecha límite
        fecha_limite = fn.NOW() - SQL('INTERVAL 5 YEAR')

        # 3. Subconsulta: Obtener los IDs de los proyectos obsoletos
        fecha_fin_antigua = Proyecto.fecha_fin < fecha_limite
        fecha_fin_definida = Proyecto.fecha_fin.is_null(False)
        subconsulta_proyectos_obsoletos = Proyecto.select(Proyecto.id_proyecto).where(
            fecha_fin_antigua & fecha_fin_definida
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

# --- 7. Eliminar Cliente y Datos Asociados ---
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

        with db.atomic():
            proyectos_del_cliente = Proyecto.select(Proyecto.id_proyecto).where(
                Proyecto.id_cliente == cliente_a_borrar
            )

            q_delete_asig = EmpleadoProyecto.delete().where(
                EmpleadoProyecto.id_proyecto.in_(proyectos_del_cliente)
            )
            asignaciones_borradas = q_delete_asig.execute()
            print(f"[Transacción] {asignaciones_borradas} asignaciones de empleados eliminadas.")

            q_delete_proy = Proyecto.delete().where(
                Proyecto.id_cliente == cliente_a_borrar
            )
            proyectos_borrados = q_delete_proy.execute()
            print(f"[Transacción] {proyectos_borrados} proyectos eliminados.")

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


if __name__ == '__main__':
    
    print("PRUEBAS - actualizacion_borrado.py")
    
    print("PRUEBA 1: Actualizar teléfono de cliente")
    actualizar_telefono_cliente('12345678A', '999999999')

    print("PRUEBA 2: Aumentar presupuesto de proyectos activos")
    if conectar_bd():
        try:
            for p in Proyecto.select():
                print(f"  - {p.titulo_proyecto}: {p.presupuesto}€")
        finally:
            cerrar_bd()
    
    print("\nAumentando presupuesto un 10% a proyectos activos...")
    aumentar_presupuesto_proyectos_activos()
    
    print("\nDespués:")
    if conectar_bd():
        try:
            for p in Proyecto.select():
                print(f"  - {p.titulo_proyecto}: {p.presupuesto}€")
        finally:
            cerrar_bd()

    print("PRUEBA 3: Reasignar jefe de proyecto")
    print("Reasignando proyecto 'App Móvil' a 'Juan Pérez' (11111111X)...")
    
    if conectar_bd():
        try:
            p = Proyecto.get_or_none(Proyecto.titulo_proyecto == 'App Móvil')
            if p:
                print(f"Jefe actual: {p.id_jefe_proyecto.nombre}")
            else:
                print("Proyecto 'App Móvil' no encontrado")
        finally:
            cerrar_bd()
    
    reasignar_jefe_proyecto(id_proyecto=2, nuevo_jefe_dni='11111111X')

    print("PRUEBA 4: Eliminar clientes sin proyectos")
    print("Clientes antes de eliminar:")
    if conectar_bd():
        try:
            for c in Cliente.select():
                proyectos = Proyecto.select().where(Proyecto.id_cliente == c)
                print(f"  - {c.nombre_cliente} ({c.dni_cif}): {proyectos.count()} proyectos")
        finally:
            cerrar_bd()
    
    print("\nEliminando clientes sin proyectos...")
    eliminar_clientes_sin_proyectos()
    
    print("\nClientes después de eliminar:")
    if conectar_bd():
        try:
            for c in Cliente.select():
                proyectos = Proyecto.select().where(Proyecto.id_cliente == c)
                print(f"  - {c.nombre_cliente} ({c.dni_cif}): {proyectos.count()} proyectos")
        finally:
            cerrar_bd()

    print("PRUEBA 5: Eliminar proyectos antiguos y baratos")
    print("Proyectos antes de eliminar:")
    if conectar_bd():
        try:
            for p in Proyecto.select():
                print(f"  - {p.titulo_proyecto}: Presupuesto={p.presupuesto}€, Fin={p.fecha_fin}")
        finally:
            cerrar_bd()
    
    print("\nEliminando proyectos con presupuesto < 10000 y fecha_fin pasada...")
    eliminar_proyectos_antiguos_baratos()
    
    print("\nProyectos después de eliminar:")
    if conectar_bd():
        try:
            for p in Proyecto.select():
                print(f"  - {p.titulo_proyecto}: Presupuesto={p.presupuesto}€, Fin={p.fecha_fin}")
        finally:
            cerrar_bd()

    print("PRUEBA 6: Transacción de limpieza (proyectos >5 años)")
    print("Ejecutando transacción con proyecto destino ID=1...")
    transaccion_limpieza_proyectos(id_proyecto_destino=1)

    print("PRUEBA 7: Eliminar cliente y datos asociados (cascada)")
    if conectar_bd():
        try:
            clientes = Cliente.select().count()
            proyectos = Proyecto.select().count()
            asignaciones = EmpleadoProyecto.select().count()
            print(f"  - Clientes: {clientes}")
            print(f"  - Proyectos: {proyectos}")
            print(f"  - Asignaciones: {asignaciones}")
        finally:
            cerrar_bd()
    
    print("\nEliminando cliente 'Empresa B' (B87654321) y sus datos...")
    eliminar_cliente_y_proyectos('B87654321')
    
    print("\nEstado después de eliminar:")
    if conectar_bd():
        try:
            clientes = Cliente.select().count()
            proyectos = Proyecto.select().count()
            asignaciones = EmpleadoProyecto.select().count()
            print(f"  - Clientes: {clientes}")
            print(f"  - Proyectos: {proyectos}")
            print(f"  - Asignaciones: {asignaciones}")
        finally:
            cerrar_bd()
    print("PRUEBAS COMPLETADAS")