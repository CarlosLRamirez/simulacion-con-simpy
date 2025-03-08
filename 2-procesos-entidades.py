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

banco = simpy.Environment()
banco.process(generator(banco, 0.1))
banco.run(until=100)

#------------------------ FIN ------------------------------------#

"""Ejesmplo 2: 2-procesos-entidades.py

Contenido y Conceptos Clave

Proceso Generador:
•	Un proceso que crea entidades (por ejemplo, clientes) de forma continua, modelando un proceso de llegada.
•	Se utiliza random.expovariate() para simular tiempos interarribo.

Proceso Entidad:
•	Cada entidad (cliente) tiene su propio proceso, donde se simula la actividad (por ejemplo, atención, espera, etc.).

Aspectos Importantes:
•	Diferenciación entre el generador (que crea entidades) y el proceso individual de cada entidad.
•	Cómo se asignan tiempos aleatorios para representar comportamientos estocásticos típicos en sistemas de colas.

Puntos a Resaltar
	•	La interacción entre el proceso generador y el proceso entidad.
	•	El uso de identificadores o nombres para distinguir entre las distintas entidades.
	•	El flujo de llegada, procesamiento (simulado con yield env.timeout()) y finalización del proceso.
"""