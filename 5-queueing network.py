#!/usr/bin/env python
#
# Simpy Example - Queueing Network
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand

# Fuente Original
# https://github.com/natawutn/simpy-tutorial

# Comentarios y traduccion: Carlos Ramirez
# Para el curso Fundamentos de Modelado y Simulación
# Universidad de San Carlos De Guatemala, Guatemala


import simpy
import random


# Generic helper class to hold information regarding to resource
# This simplifies how we pass information from main program to entity process
class Server(object):
    def __init__(self, env, name, capacity, service_rate):
        self.name = name
        self.env = env
        self.service_rate = service_rate
        self.capacity = capacity
        self.resource = simpy.Resource(env, capacity=capacity)

    def print_stats(self):
        print('\t[{}] {} using, {} in queue'.format(self.name, self.resource.count, len(self.resource.queue)))

    def get_service_time(self):
        return random.expovariate(self.service_rate)


# ---------------------------
# Proceso: Pasajero (entidad)
# ---------------------------
# Este proceso (entidad) representa el ciclo de vida de un cliente en el sistema.
# El cliente llega, compra un ticket en la taquilla, luego se va a la puerta de abordaje.

def passenger(env, name, ticket_office, gate):

    # El pasajero llega al sistema
    print('[{:6.2f}:{}] - arrive at the station'.format(env.now, name))

    # El pasajero compra su ticket de la taquilla
    t_arrival = env.now  #tiempo de llegada del pasajero

    # El pasajero se forma para solicitar el recurso (taquilla)
    print('[{:6.2f}:{}] - join queue at ticket office'.format(t_arrival, name))
    
    ticket_office.print_stats()
    
    #Solicitud del recurso (taquilla)
    with ticket_office.resource.request() as request:
        yield request

        # Aqui ya salio de la cola, empezó a ser atendido
        # Calculo del tiempo en cola: tiempo actual - tiempo de llegada
        t_queue = env.now - t_arrival
        print('[{:6.2f}:{}] - reach counter after waiting for {:4.2f} time units'.format(env.now, name, t_queue))
        
        # Obtener el tiempo de servicio de la taquilla
        service_time = ticket_office.get_service_time()

        # Pausa por el tiempo de Servicio
        yield env.timeout(service_time)

        # Finaliza de comprar el ticket en la taquilla
        print('[{:6.2f}:{}] - finish buying ticket after {:4.2f} time units'.format(env.now, name, service_time))

    # luego de terminar de comprar el ticket se dirige a la puerta
    # registramos el tiempo de llegada a puerta
    t_arrival = env.now
    print('[{:6.2f}:{}] - join queue at the gates'.format(t_arrival, name))
    
    gate.print_stats()
    with gate.resource.request() as request:
        yield request
        t_queue = env.now - t_arrival
        print('[{:6.2f}:{}] - reach the gate after waiting for {:4.2f} time units'.format(env.now, name, t_queue))
        service_time = gate.get_service_time()
        yield env.timeout(service_time)
        print('[{:6.2f}:{}] - pass the gate after {:4.2f} time units'.format(env.now, name, service_time))

    print('[{:6.2f}:{}] - depart from station'.format(env.now, name))


# generator - Supporting Process
# Create new passenger and then sleep for random amount of time
def passenger_generator(env, ticket_office, gate, arrival_rate):
    i = 0
    while True:
        ename = 'Passenger#{}'.format(i)
        env.process(passenger(env, ename, ticket_office, gate))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1


#------------------- Configuración de la simulación -------------------#

MEAN_INTER_ARRIVAL_TIME = 10     # 10 time units between arrivals
TO_MEAN_SERVICE_TIME = 8        # 8 time units for each service at the ticket office
GA_MEAN_SERVICE_TIME = 8        # 8 time units for each service at the gate
SIMULATION_END_TIME = 50

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
to_service_rate = 1/TO_MEAN_SERVICE_TIME
ga_service_rate = 1/GA_MEAN_SERVICE_TIME

# Definición del Entorno (Evironment)
env = simpy.Environment()

# Definción del recurso ticket_office (taquilla)
ticket_office = Server(env, 'ticket_office', 1, to_service_rate)

# Definición del recurso gate (puerta)
gate = Server(env, 'gate', 1, ga_service_rate)

# Programación del proceso de generación de pasajeros
env.process(passenger_generator(env, ticket_office, gate, arrival_rate))

# Inicio de la simulación
env.run(until=SIMULATION_END_TIME)

#------------------------- Fin ------------------------------------#

