#!/usr/bin/env python

# Ejemplo Simple con Simpy
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand

# Fuente Original
# https://github.com/natawutn/simpy-tutorial

# Comentarios y traduccion: Carlos Ramirez
# Para el curso Fundamentos de Modelado y Simulación
# Universidad de San Carlos De Guatemala, Guatemala


import simpy
from simpy.util import start_delayed

# Definición de un proceso (simple_process)
# El proceso hace una pausa dentro de la simulación
def simple_process(env, name, waitfor=50):
    print('{:6.2f}:{} - inicia proceso'.format(env.now, name))
    #Ceder el control al entorno de simulacion, para hacer una pausa
    yield env.timeout(waitfor)
    print('{:6.2f}:{} - finaliza proceso'.format(env.now, name))

# Rutina principal, configuración de la simulación
# -------------------------------------------------

# Creacion del entorno de la simulación
env = simpy.Environment()

# Programacion de una instancia del proceso
proc = env.process(simple_process(env, 'Proceso 1'))
# Programación de otra instancia del proceso (la cual iniciará retrasada)
#proc2 = start_delayed(env, simple_process(env, 'Proceso 2', waitfor=60), 10)
# Programación de una tercera instancia del proceso
#proc3 = env.process(simple_process(env,'Proceso 3',waitfor=15))
# Ejecución de la simulación
env.run()

#------------------------ FIN ------------------------------------#

"""
Ejemplo 1: 1-ejemplo-simple.py

•	Introducción a SimPy:
•	Se crea un entorno de simulación (simpy.Environment()).
•	Los procesos se definen como funciones generadoras utilizando yield env.timeout(...).

Descripción del Ejemplo:
•	Se lanza un proceso simple que muestra cómo se inicia, espera un determinado tiempo y finaliza.
•	Se utiliza para introducir conceptos básicos: tiempo de simulación, uso de env.now, y la mecánica de pausar la ejecución con yield.

Puntos a Resaltar
•	La importancia del entorno en SimPy.
•	Cómo se utiliza yield para simular la espera de un proceso.
•	El formato de salida que indica el avance del tiempo de simulación.

"""
