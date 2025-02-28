#!/usr/bin/env python
#
# Simpy Example - Processes
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand

# Fuente Original
# https://github.com/natawutn/simpy-tutorial

# Comentarios y Traducción a Español: Carlos Ramirez, Universidad de San Carlos De Guatemala, Guatemala


import simpy
import random


# entidad - Proceso de tipo entidad
# Describe el comportamiento de la entidad a lo largo de la simulación
def entity(env, name, waitfor=50):
    print('[{:6.2f}:{}] - inicio del proceso'.format(env.now, name))
    yield env.timeout(waitfor)
    print('[{:6.2f}:{}] - fin del proceso'.format(env.now, name))


# generador - Proceso de Soporte
# Crea una nueva entidad y luego se "duerme" por un tiempo determinado
def generator(env, arrival_rate):
    i = 0
    while True:
        #Nombre de la entidad
        ename = 'Entidad#{}'.format(i)
        print('[{:6.2f}:Generador] Genera {}'.format(env.now, ename))

        #Se programa la ejecución del procesopara la entidad
        env.process(entity(env, ename))

        #Se obtiene el tiempo para generar la siguiente entidad en base a una distribución exponencial
        next_entity_arrival = random.expovariate(arrival_rate)
        print('[{:6.2f}:Generador] la siguiente generación sera en {} segundos'.format(env.now, next_entity_arrival))
        
        #Pausa (dormir) el tiempo aleatorio obtenido previamente.
        yield env.timeout(next_entity_arrival)
        i += 1


## Preparación de la simulación

env = simpy.Environment()
env.process(generator(env, 0.1))
env.run(until=100)


