from peewee import *
from conexion import conectar_bd, cerrar_bd
from crear_tablas import Cliente, Empleado, Proyecto, EmpleadoProyecto
import datetime

def consulta_1():
    print("\n--- 1. Presupuesto total de los proyectos de cada cliente ---")
    # Usamos backref 'proyectos' definido en Proyecto.id_cliente
    clientes = Cliente.select()
    for cliente in clientes:
        total_presupuesto = 0
        # Iteramos sobre los proyectos del cliente usando el backref
        for proyecto in cliente.proyectos:
            total_presupuesto += proyecto.presupuesto
        
        print(f"Cliente: {cliente.nombre_cliente} | Presupuesto Total: {total_presupuesto}")

def consulta_2():
    print("\n--- 2. Empleados asignados a cada proyecto y número total de proyectos en los que participan ---")
    proyectos = Proyecto.select()
    for proyecto in proyectos:
        print(f"Proyecto: {proyecto.titulo_proyecto}")
        # Usamos backref 'asignaciones' definido en EmpleadoProyecto.id_proyecto
        for asignacion in proyecto.asignaciones:
            empleado = asignacion.id_empleado
            # Usamos backref 'participaciones' definido en EmpleadoProyecto.id_empleado para contar
            num_proyectos = empleado.participaciones.count()
            print(f"  - Empleado: {empleado.nombre} | Total Proyectos: {num_proyectos}")

def consulta_3():
    print("\n--- 3. Proyecto con el presupuesto más alto de cada cliente ---")
    clientes = Cliente.select()
    for cliente in clientes:
        proyecto_mas_caro = None
        max_presupuesto = -1
        
        for proyecto in cliente.proyectos:
            if proyecto.presupuesto > max_presupuesto:
                max_presupuesto = proyecto.presupuesto
                proyecto_mas_caro = proyecto
        
        if proyecto_mas_caro:
            print(f"Cliente: {cliente.nombre_cliente} | Proyecto Más Caro: {proyecto_mas_caro.titulo_proyecto} ({max_presupuesto})")
        else:
            print(f"Cliente: {cliente.nombre_cliente} | Sin proyectos")

def consulta_4():
    print("\n--- 4. Listar todos los proyectos con su jefe de proyecto y el número de empleados asignados ---")
    proyectos = Proyecto.select()
    for proyecto in proyectos:
        jefe = proyecto.id_jefe_proyecto
        # Contamos las asignaciones usando el backref 'asignaciones'
        num_empleados = proyecto.asignaciones.count()
        print(f"Proyecto: {proyecto.titulo_proyecto} | Jefe: {jefe.nombre} | Num Empleados: {num_empleados}")

def consulta_5():
    print("\n--- 5. Proyecto más largo de cada cliente con el total de empleados que han trabajado en él ---")
    clientes = Cliente.select()
    for cliente in clientes:
        proyecto_mas_largo = None
        max_duracion = -1
        
        for proyecto in cliente.proyectos:
            if proyecto.fecha_fin and proyecto.fecha_inicio:
                duracion = (proyecto.fecha_fin - proyecto.fecha_inicio).days
                if duracion > max_duracion:
                    max_duracion = duracion
                    proyecto_mas_largo = proyecto
            else:
                # Si no tiene fecha fin, podríamos considerar la fecha actual o ignorarlo.
                # Para este ejercicio, si falta fecha, no calculamos duración o asumimos 0.
                pass
        
        if proyecto_mas_largo:
            num_empleados = proyecto_mas_largo.asignaciones.count()
            print(f"Cliente: {cliente.nombre_cliente} | Proyecto Más Largo: {proyecto_mas_largo.titulo_proyecto} ({max_duracion} días) | Empleados: {num_empleados}")
        else:
             print(f"Cliente: {cliente.nombre_cliente} | Sin proyectos o sin fechas válidas")

if __name__ == "__main__":
    if conectar_bd():
        try:
            consulta_1()
            consulta_2()
            consulta_3()
            consulta_4()
            consulta_5()
        finally:
            cerrar_bd()
