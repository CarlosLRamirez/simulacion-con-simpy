#!/usr/bin/env python
#
# Ejemplo Simpy - Procesos y entidades
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand

# Fuente Original
# https://github.com/natawutn/simpy-tutorial

# Comentarios y traduccion: Carlos Ramirez
# Para el curso Fundamentos de Modelado y Simulación
# Universidad de San Carlos De Guatemala, Guatemala

# Codigo modificado el ejemplo: 3-recursos para agregar lo siguiente:
# Ejercicio 1: Cálculo de Tiempos Promedio en Cola y en el Sistema
# Ejercicio 2: Cálculo de la Utilización del Servidor (ρ)

import simpy
import random

tiempoEnCola = []
tiempoEnSistema = []
tiempoOcupado = []

# Funcion para imprimir el estado del recurso (taquilla)
def print_stats(resource):
    print('\t[Recurso] {} ocupado, {} en cola'.format(resource.count, len(resource.queue)))


# Proceso Entidad: Pasajero
# Este proceso describe el comportamiento de un pasajero al llegar a la taquilla.
def passenger(env, name, server, service_rate):
    
    global tiempoEnCola, tiempoEnSistema, tiempoOcupado

    # El pasajero llega a la estación y se imprime el estado actual del recurso.
    print('[{:6.2f}:{}] - llega a la estación'.format(env.now, name))
    t_llegada = env.now
    print_stats(server)
    
    # En esta parte se solicita el recurso (taquilla).
    # El pasajero espera (se pone en cola) hasta que el recurso esté disponible.
    with server.request() as request:
        yield request  # Pausa la ejecución hasta que se le asigne el recurso.
        print('[{:6.2f}:{}] - inicia la compra del ticket'.format(env.now, name))
        print_stats(server)
        t_inicio=env.now
        
        # Se genera un tiempo de servicio aleatorio basado en la tasa de servicio.
        service_time = random.expovariate(service_rate)
        yield env.timeout(service_time)  # Pausa el proceso durante el tiempo de servicio.
        print('[{:6.2f}:{}] - finaliza la compra del ticket'.format(env.now, name))
        print_stats(server)
        t_salida=env.now
        
        # Al salir del bloque 'with', el recurso se libera automáticamente.
    
    # Una vez liberado el recurso, el pasajero sale de la estación.
    print('[{:6.2f}:{}] - sale de la estación'.format(env.now, name))
    print_stats(server)
    tiempoEnCola.append(t_inicio-t_llegada)
    tiempoEnSistema.append(t_salida-t_inicio)
    tiempoOcupado.append(t_salida-t_inicio)


# generador - Proceso de Soporte
# Crea una nueva entidad y luego se "duerme" por un tiempo determinado
def passenger_generator(env, server, arrival_rate, service_rate):
    i = 0
    while True:
        ename = 'Pasajero#{}'.format(i)
        env.process(passenger(env, ename, server, service_rate))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1

# Rutina principal
# ------------------------------------

#Configuración de la simulación

# for simplicidad, definimos las tasas de llegada y servicio  como tiempo promedio entre llegadas y tiempo promedio de servicio

MEAN_INTER_ARRIVAL_TIME = 4     # 5 time units between arrivals (1/lambda)
MEAN_SERVICE_TIME = 7           # 4 time units for each service (1/mu)
SIMULATION_END_TIME = 840

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME # lambda 
service_rate = 1/MEAN_SERVICE_TIME # Mu

env = simpy.Environment()
taquilla = simpy.Resource(env, capacity=1)
env.process(passenger_generator(env, taquilla, arrival_rate, service_rate))
env.run(until=SIMULATION_END_TIME)


#Calculo de Metricas
wq=sum(tiempoEnCola)/len(tiempoEnCola)
w=sum(tiempoEnSistema)/len(tiempoEnSistema)
rho=sum(tiempoOcupado)/SIMULATION_END_TIME

print('\n------ Resultados de la simulacion -------')
print(f'Promedio de espera en cola (W_q):       {wq:.4f}')
print(f'Promedio total en el sistema (W):       {w:.4f}')
print(f'Ocupacion del cajero (rho):             {rho:.4f}')
#------------------------ FIN ------------------------------------#


"""
Simulación de un sistema de recursos usando SimPy

Este script modela un escenario donde se simula el funcionamiento de un servicio de taquilla (ticket office)
utilizando el framework SimPy. La simulación se enfoca en la gestión de recursos y el comportamiento de
los procesos (pasajeros) que interactúan con el recurso (la taquilla).

Aspectos clave de la simulación:
  - Los pasajeros llegan al sistema de forma aleatoria, con tiempos interarribo generados mediante una distribución exponencial.
  - Cada pasajero, al llegar, solicita el servicio de la taquilla. Si el recurso está ocupado, el pasajero se une a la cola.
  - Una vez que se le asigna el recurso, el pasajero es atendido por un tiempo de servicio también determinado de forma exponencial.
  - Se imprimen mensajes en cada etapa del proceso para mostrar el estado del sistema, incluyendo el número de clientes
    en cola y el estado del recurso (cuántos cajeros están ocupados).
  - La simulación finaliza después de un tiempo total definido, permitiendo analizar el comportamiento y la utilización del recurso.

Fuente original: https://github.com/natawutn/simpy-tutorial
Comentarios y traducción: Carlos Ramirez, Universidad de San Carlos de Guatemala

Este ejemplo sirve para entender cómo modelar y simular un sistema de colas M/M/1 utilizando SimPy, siendo útil
para cursos de Fundamentos de Modelado y Simulación.
"""