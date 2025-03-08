"""
Simulación de un sistema de colas M/M/1 utilizando SimPy.

Este script simula el funcionamiento de un banco (o sistema similar) con un servidores (cajero).
- Los clientes llegan al sistema de acuerdo a una distribución exponencial con tasa LAMBDA.
- El tiempo de servicio también se genera de forma exponencial con tasa MU.

Durante la simulación se registran y calculan las siguientes métricas:
  - Utilización del servidor (rho), calculada como el tiempo total en que el servidor está ocupados 
    dividido por el tiempo total de simulación.
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

SIM_TIME = 50        #Tiempo total de simulación
LAMBDA = 1/2          # Taza de llegadas (por unidad de tiempo)
MU = 1/4              # Taza de servicio (por unidad de tiempo)

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
def generacion_llegadas(env,server):
    id_cliente = 0

    #Este bucle se ejecuta indefinidamente hasta el final de la simulación
    while True:
        tiempo_entre_llegadas = random.expovariate(LAMBDA)
        yield env.timeout(tiempo_entre_llegadas)
        id_cliente+=1
        #print(f"{env.now:.4f}: Se generó el cliente {id_cliente:d}. Tiempo entre llegadas {tiempo_entre_llegadas:.4f}")
        tiempo_llegada=env.now
        env.process(atencion_cliente(env,id_cliente,server,tiempo_llegada))

# ---------------------------
# Proceso: llegada_Cliente
# ---------------------------
# Este proceso (entidad) representa el ciclo de vida de un cliente en el sistema.
# El cliente llega, solicita atención del cajero (o se pone en la cola), es atendido durante un
# tiempo determinado y luego sale del sistema.
def atencion_cliente(env,id_cliente,server,tiempo_llegada):
    
    global area_clientes_cola, area_clientes_sistema, tiempo_ultimo_evento,tiempo_ocupado, total_cola, total_sistema, total_clientes_simulacion
    
    print(f"{id_cliente:d},{env.now:.2f},LlegadaCliente,{len(server.queue):d},{server.count:d},{tiempo_ultimo_evento:.4f}")
    actualizar_estadisticas(env,server)

    #Esta es la parte mas importante del proceso, aqui solicitamos el servidor, el proceso continua hasta que exista un servidor disponible
    #Esto es gestionado por Simpy
    with server.request() as request: 
        yield request 
        #Inicio del servicio
        print(f"{id_cliente:d},{env.now:.2f},InicioServicio,{len(server.queue):d},{server.count:d},{tiempo_ultimo_evento:.4f}")

        #Generación del tiempo de servicio aleatorio (distribución exponencial)
        tiempo_servicio = random.expovariate(MU)
        
        #Captura del inicio del servicio
        inicio_servicio = env.now
        
        #Calculo del tiempo que estuvo el cleinte en cola
        total_cola += inicio_servicio - tiempo_llegada

        actualizar_estadisticas(env,server)

        #delay por el tiempo de servicio
        yield env.timeout(tiempo_servicio)

        #Captura del tiempo que el cliente estuvo siendo atendido, lo cual equivale a que el cajero estuvo ocupado
        tiempo_ocupado += env.now - inicio_servicio

        print(f"{id_cliente:d},{env.now:.2f},FinServicio(Salida),{len(server.queue):d},{server.count:d},{tiempo_ultimo_evento:.4f}")

        actualizar_estadisticas(env,server)

        #Captura el fin del servicio
        fin_servicio=env.now

        #Calculo del total de tiempo que el cleinte estuvo en el sistema
        total_sistema += fin_servicio-tiempo_llegada

        #Registro de los clientes que van completando el servicio y saliendo del sistema
        #esto nos sirve la final para calcular el tiempo promedio que estuvieron los cleintes en cola y en el sistema
        #durante toda la simulación
        total_clientes_simulacion +=1

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

    #random.seed(RANDOM_SEED)
    banco = simpy.Environment()
    cajero = simpy.Resource(banco, capacity=1)
    banco.process(generacion_llegadas(banco,cajero))
    print("\n--- Tabla de Eventos ---")
    print("Num,Timestamp,Tipo Evento,Tamaño de la Cola,Cajeros Ocupados,Tiempo desde evento anterior")

    banco.run(until=SIM_TIME)

    #Calculo de resultados 
    utilizacion = (tiempo_ocupado / (SIM_TIME))*100
    L = area_clientes_sistema/SIM_TIME
    L_q=area_clientes_cola/SIM_TIME
    Wq=total_cola / total_clientes_simulacion
    W=total_sistema / total_clientes_simulacion

    #Despliegue de resultados de la simulación
    print("\n--- Resultados de la Simulación ---")
    print(f"Utilizacion del Servidor:                     {utilizacion:.2f}%")
    print(f"Numero de clientes promedio en el banco (L):  {L:.4f}")
    print(f"Numero de clientes promedio en cola (L_q):    {L_q:.4f}")
    print(f"Tiempo promedio de espera en el sistema (W):  {W:.4f}")
    print(f"Tiempo promedio de espera en la cola (Wq):    {Wq:.4f}")


if __name__ == '__main__':
    main()

