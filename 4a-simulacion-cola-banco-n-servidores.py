#!/usr/bin/env python

"""
Simulación de un sistema de colas M/M/c utilizando SimPy.

Este script simula el funcionamiento de un banco (o sistema similar) con múltiples servidores (cajeros).
- Los clientes llegan al sistema de acuerdo a una distribución exponencial con tasa LAMBDA.
- El tiempo de servicio también se genera de forma exponencial con tasa MU.
- Se puede configurar el número de servidores mediante NUM_SERVIDORES.
- Durante la simulación, se genera un archivo de salida llamado "eventos_simulacion.csv" que registra 
  los eventos ocurridos, como llegadas, inicios y finales de servicio, junto con información relevante 
  como el tamaño de la cola y el número de cajeros ocupados.
  
Durante la simulación se registran y calculan las siguientes métricas:
  - Utilización del servidor (rho), calculada como el tiempo total en que los servidores están ocupados 
    dividido por el tiempo total de simulación multiplicado por el número de servidores.
  - Número promedio de clientes en el sistema (L) y en la cola (L_q), mediante el área bajo la curva 
    de la cantidad de clientes.
  - Tiempo promedio en el sistema (W) y tiempo promedio de espera en la cola (Wq).

Se imprime una tabla de eventos y, al final, se muestran los resultados de la simulación.
"""

#Estructura básica de la simulación
import simpy
import random
import numpy as np
import matplotlib.pyplot as plt


#RANDOM_SEED = 1717
SIM_TIME = 480        #Tiempo total de simulación
LAMBDA = 1          # Taza de llegadas (por unidad de tiempo)
MU = 0.25              # Taza de servicio (por unidad de tiempo)
NUM_SERVIDORES = 5   # Numero de servidores en el sistema

# Tiempo máximo de llegada de clientes (8 horas)
TIEMPO_LLEGADA_MAXIMA = SIM_TIME  # 480 minutos (8 horas)

#Variables Globales
tiempo_ultimo_evento = 0.0
area_clientes_cola   = 0.0
area_clientes_sistema = 0.0
tiempo_ocupado = 0.0
total_cola = 0.0
total_sistema = 0.0
total_clientes_simulacion = 0


# ---------------------------
# Proceso: generacion_llegadas
# ---------------------------
# Este proceso genera clientes que van entrando al sistema
# Los tiempos entre llegadas estan distribuidos exponencialmente 
def generacion_llegadas(env, server):
    id_cliente = 0

    #Este bucle se ejecuta indefinidamente hasta el final de la simulación
    while True:
        tiempo_entre_llegadas = random.expovariate(LAMBDA)
        yield env.timeout(tiempo_entre_llegadas)

        # Detener la generación de clientes después de TIEMPO_LLEGADA_MAXIMA
        if env.now > TIEMPO_LLEGADA_MAXIMA:
            break

        id_cliente += 1
        tiempo_llegada = env.now
        env.process(atencion_cliente(env, id_cliente, server, tiempo_llegada))

# ---------------------------
# Proceso: atención_cliente
# ---------------------------
# Este proceso (entidad) representa el ciclo de vida de un cliente en el sistema.
# El cliente llega, solicita atención del cajero (o se pone en la cola), es atendido durante un
# tiempo determinado y luego sale del sistema.
def atencion_cliente(env, id_cliente, server, tiempo_llegada):
    global area_clientes_cola, area_clientes_sistema, tiempo_ultimo_evento, tiempo_ocupado, total_cola, total_sistema, total_clientes_simulacion

    # Calcular tiempo desde la última llegada
    tiempo_desde_ultima_llegada = env.now - tiempo_ultimo_evento

    # Registrar el evento de llegada en el archivo unificado
    with open("eventos_simulacion.csv", "a") as archivo_eventos:
        archivo_eventos.write(f"{id_cliente},Llegada,{env.now:.2f},{tiempo_desde_ultima_llegada:.2f},{len(server.queue)},{server.count},,,,,\n")

    # Actualizar estadísticas después de la llegada
    actualizar_estadisticas(env, server)

    # Solicitar el servidor
    with server.request() as request:
        yield request

        # Registrar el inicio del servicio
        tiempo_inicio_servicio = env.now
        tiempo_en_cola = tiempo_inicio_servicio - tiempo_llegada
        with open("eventos_simulacion.csv", "a") as archivo_eventos:
            archivo_eventos.write(f"{id_cliente},InicioServicio,{env.now:.2f},,,{len(server.queue)},{server.count},,,,,\n")

        # Generar tiempo de servicio y simular el tiempo de atención
        tiempo_servicio = random.expovariate(MU)
        yield env.timeout(tiempo_servicio)

        # Registrar el evento de fin de servicio en el archivo unificado
        tiempo_fin_servicio = env.now
        tiempo_total = tiempo_fin_servicio - tiempo_llegada
        with open("eventos_simulacion.csv", "a") as archivo_eventos:
            archivo_eventos.write(f"{id_cliente},FinServicio,{tiempo_fin_servicio:.2f},,,{len(server.queue)},{server.count},{tiempo_inicio_servicio:.2f},{tiempo_fin_servicio:.2f},{tiempo_en_cola:.2f},{tiempo_servicio:.2f},{tiempo_total:.2f}\n")

        # Actualizar estadísticas después del fin del servicio
        tiempo_ocupado += tiempo_servicio
        total_cola += tiempo_en_cola
        total_sistema += tiempo_total
        total_clientes_simulacion += 1
        actualizar_estadisticas(env, server)

# ---------------------------
# Función para actualizar las estadisticas
# ---------------------------
# Esta función calcula el tiempo transcurrido desde el último evento y actualiza el área acumulada bajo la curva para el 
# número de clientes en cola (area_clientes_cola) y en el sistema (area_clientes_sistema).
def actualizar_estadisticas(env,server):

    global area_clientes_cola, area_clientes_sistema, tiempo_ultimo_evento
    delta_tiempo = env.now - tiempo_ultimo_evento

    clientes_cola = len(server.queue)
    cajeros_ocupados = server.count
    clientes_sistema = clientes_cola+cajeros_ocupados

    area_clientes_cola+=clientes_cola*delta_tiempo
    area_clientes_sistema+=clientes_sistema*delta_tiempo
    

    tiempo_ultimo_evento = env.now


# ---------------------------
# Configuración General de la simulación
# ---------------------------
def main():

    global area_clientes_cola, area_clientes_sistema, total_sistema, total_cola, total_clientes_simulacion

    # Crear encabezados para el archivo unificado
    with open("eventos_simulacion.csv", "w") as archivo_eventos:
        archivo_eventos.write("ID_Cliente,Evento,Tiempo,Tiempo_Desde_Ultima_Llegada,Tamaño_Cola,Cajeros_Ocupados,Tiempo_Inicio_Servicio,Tiempo_Fin_Servicio,Tiempo_En_Cola,Tiempo_En_Servicio,Tiempo_Total\n")

    banco = simpy.Environment()

    #Instancia del recurso: cajero
    cajero = simpy.Resource(banco, capacity=NUM_SERVIDORES)

    #Programamos el recurso de generación de llegas de clientes
    banco.process(generacion_llegadas(banco, cajero))
    print("\n--- Tabla de Eventos ---")
    print("Num,Timestamp,Tipo Evento,Tamaño de la Cola,Cajeros Ocupados,Tiempo desde evento anterior")

    # Ejecutar la simulación hasta que no haya más clientes en el sistema
    while True:
        banco.run()  # Ejecutar la simulación indefinidamente
        if len(cajero.queue) == 0 and cajero.count == 0:  # Verificar si no hay clientes en cola o siendo atendidos
            break

    #Calculo de resultados 
    utilizacion = (tiempo_ocupado / (banco.now * NUM_SERVIDORES)) * 100
    L = area_clientes_sistema / banco.now
    L_q = area_clientes_cola / banco.now
    Wq = total_cola / total_clientes_simulacion
    W = total_sistema / total_clientes_simulacion

    #Despliegue de resultados de la simulación
    print("\n--- Resultados de la Simulación ---")
    print(f"Utilizacion del Servidor:                     {utilizacion:.2f}%")
    print(f"Numero de clientes promedio en el banco (L):  {L:.4f}")
    print(f"Numero de clientes promedio en cola (L_q):    {L_q:.4f}")
    print(f"Tiempo promedio de espera en el sistema (W):  {W:.4f}")
    print(f"Tiempo promedio de espera en la cola (Wq):    {Wq:.4f}")


if __name__ == '__main__':
    main()

