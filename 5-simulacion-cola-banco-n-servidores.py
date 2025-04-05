#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simulación de un sistema de colas M/M/c utilizando SimPy.

Este script simula el funcionamiento de un banco (o sistema similar) con múltiples servidores (cajeros).
- Los clientes llegan al sistema de acuerdo a una distribución exponencial con tasa LAMBDA.
- El tiempo de servicio también se genera de forma exponencial con tasa MU.
- Se puede configurar el número de servidores mediante NUM_SERVIDORES.
- Durante la simulación, se genera un archivo de salida llamado "eventos_simulacion.csv" que registra 
  los eventos ocurridos, como llegadas, inicios y finales de servicio, junto con información relevante 
  como el tamaño de la cola y el número de cajeros ocupados.
"""

# Estructura básica de la simulación
import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la simulación
TIEMPO_LLEGADA_MAXIMA = 480        #  Tiempo total de apertura del banco (unidades de tiempo)
LAMBDA = 1                          # Tasa de llegadas (por unidad de tiempo)
MU = 0.25                           # Tasa de servicio (por unidad de tiempo)
NUM_SERVIDORES = 5                  # Número de servidores en el sistema


# Variables globales
tiempo_ultimo_evento = 0.0
area_clientes_cola = 0.0
area_clientes_sistema = 0.0
tiempo_ocupado = 0.0
total_cola = 0.0
total_sistema = 0.0
total_clientes_simulacion = 0

# ---------------------------
# Función para actualizar las estadísticas
# ---------------------------
def actualizar_estadisticas(env, server, id_cliente=None, evento=None, tiempo_inicio_servicio=None, tiempo_fin_servicio=None, tiempo_en_cola=None, tiempo_servicio=None, tiempo_total=None):
    global area_clientes_cola, area_clientes_sistema, tiempo_ultimo_evento
    delta_tiempo = env.now - tiempo_ultimo_evento

    clientes_cola = len(server.queue)
    cajeros_ocupados = server.count
    clientes_sistema = clientes_cola + cajeros_ocupados

    area_clientes_cola += clientes_cola * delta_tiempo
    area_clientes_sistema += clientes_sistema * delta_tiempo

    tiempo_ultimo_evento = env.now

    # Quitar el Tiempo_en_Cola en el evento FinServicio
    if evento == "FinServicio":
        tiempo_en_cola = ""
    
    # Registrar el evento en el archivo CSV
    with open("eventos_simulacion.csv", "a") as archivo_eventos:
        archivo_eventos.write(f"{id_cliente if id_cliente else ''},{evento if evento else ''},{env.now:.2f},{delta_tiempo:.2f},{clientes_cola},{cajeros_ocupados},{tiempo_inicio_servicio if tiempo_inicio_servicio else ''},{tiempo_fin_servicio if tiempo_fin_servicio else ''},{tiempo_en_cola if tiempo_en_cola else ''},{tiempo_servicio if tiempo_servicio else ''},{tiempo_total if tiempo_total else ''}\n")

# ---------------------------
# Proceso: atención al cliente
# ---------------------------
def atencion_cliente(env, id_cliente, server, tiempo_llegada):
    global tiempo_ocupado, total_cola, total_sistema, total_clientes_simulacion

    # Actualizar estadísticas y registrar llegada
    actualizar_estadisticas(env, server, id_cliente=id_cliente, evento="Llegada")

    # Solicitar el servidor
    with server.request() as request:
        yield request

        # Registrar el inicio del servicio
        tiempo_inicio_servicio = env.now
        tiempo_en_cola = tiempo_inicio_servicio - tiempo_llegada
        actualizar_estadisticas(env, server, id_cliente=id_cliente, evento="InicioServicio", tiempo_inicio_servicio=tiempo_inicio_servicio, tiempo_en_cola=tiempo_en_cola)

        # Generar tiempo de servicio y simular el tiempo de atención
        tiempo_servicio = random.expovariate(MU)
        yield env.timeout(tiempo_servicio)

        # Registrar el evento de fin de servicio
        tiempo_fin_servicio = env.now
        tiempo_total = tiempo_fin_servicio - tiempo_llegada
        actualizar_estadisticas(env, server, id_cliente=id_cliente, evento="FinServicio", tiempo_inicio_servicio=tiempo_inicio_servicio, tiempo_fin_servicio=tiempo_fin_servicio, tiempo_en_cola=tiempo_en_cola, tiempo_servicio=tiempo_servicio, tiempo_total=tiempo_total)

        # Actualizar estadísticas después del fin del servicio
        tiempo_ocupado += tiempo_servicio
        total_cola += tiempo_en_cola
        total_sistema += tiempo_total
        total_clientes_simulacion += 1

# ---------------------------
# Proceso: generación de llegadas
# ---------------------------
def generacion_llegadas(env, server):
    id_cliente = 0

    while env.now <= TIEMPO_LLEGADA_MAXIMA:
        tiempo_entre_llegadas = random.expovariate(LAMBDA)
        yield env.timeout(tiempo_entre_llegadas)

        id_cliente += 1
        tiempo_llegada = env.now
        env.process(atencion_cliente(env, id_cliente, server, tiempo_llegada))

# ---------------------------
# Configuración General de la simulación
# ---------------------------
def main():
    global area_clientes_cola, area_clientes_sistema, total_sistema, total_cola, total_clientes_simulacion

    # Crear encabezados para el archivo unificado
    with open("eventos_simulacion.csv", "w") as archivo_eventos:
        archivo_eventos.write("ID_Cliente,Evento,Tiempo,Tiempo_Desde_Ultima_Llegada,Tamaño_Cola,Cajeros_Ocupados,Tiempo_Inicio_Servicio,Tiempo_Fin_Servicio,Tiempo_En_Cola,Tiempo_En_Servicio,Tiempo_Total\n")

    banco = simpy.Environment()

    # Instancia del recurso: cajero
    cajero = simpy.Resource(banco, capacity=NUM_SERVIDORES)

    # Programamos el recurso de generación de llegadas de clientes
    banco.process(generacion_llegadas(banco, cajero))
    print("\n--- Tabla de Eventos ---")
    print("Num,Timestamp,Tipo Evento,Tamaño de la Cola,Cajeros Ocupados,Tiempo desde evento anterior")

    # Ejecutar la simulación hasta que no haya más clientes en el sistema
    while True:
        banco.run()  # Ejecutar la simulación indefinidamente
        if len(cajero.queue) == 0 and cajero.count == 0:  # Verificar si no hay clientes en cola o siendo atendidos
            break

    # Calculo de resultados
    utilizacion = (tiempo_ocupado / (banco.now * NUM_SERVIDORES)) * 100
    L = area_clientes_sistema / banco.now
    L_q = area_clientes_cola / banco.now
    Wq = total_cola / total_clientes_simulacion
    W = total_sistema / total_clientes_simulacion

    # Despliegue de resultados de la simulación
    print("\n--- Resultados de la Simulación ---")
    print(f"Utilizacion del Servidor:                     {utilizacion:.2f}%")
    print(f"Numero de clientes promedio en el banco (L):  {L:.4f}")
    print(f"Numero de clientes promedio en cola (L_q):    {L_q:.4f}")
    print(f"Tiempo promedio de espera en el sistema (W):  {W:.4f}")
    print(f"Tiempo promedio de espera en la cola (Wq):    {Wq:.4f}")


if __name__ == '__main__':
    main()

