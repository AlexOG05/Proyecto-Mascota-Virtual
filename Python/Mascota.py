"""
Clase Mascota
Autor: Alex Ortiz García
"""

import time

class Mascota():

    # Constantes
    MAX_HUNGER = 100
    MAX_HAPPY = 100

    # Constructor
    def __init__(self, name):
        # Atributos privados
        self.__name = name
        self.__health = 100
        self.__happy = 70
        self.__hunger = 70
        self.__age = 0
        self.__alive = True
        self.__last_upd = time.time()

    # toString
    def __str__(self):
        if not self.__alive:
            return f"{self.__name} no sigue entre nosotros..."
        else:
            return (f"Estado {self.__name}\n"
                    f"Vida: {self.__health}\n"
                    f"Felicidad: {self.__happy}%\n"
                    f"Hambre: {self.__hunger}%\n"
                    f"Edad: {self.__age} años\n")

    # Getters
    @property
    def nombre(self):
        return self.__name

    @property
    def vida(self):
        return self.__health

    @property
    def felicidad(self):
        return self.__happy

    @property
    def hambre(self):
        return self.__hunger

    @property
    def edad(self):
        return self.__age

    @property
    def vivo(self):
        return self.__alive

    # Métodos Funcionales
    def actualizar(self):
        # Actualizar el tiempo
        now = time.time()
        time_pass = now - self.__last_upd

        # Reducir hambre y felicidad segun tiempo pasado
        self.__hunger -= time_pass // 10
        self.__happy -= time_pass // 10

        # Evitar que hambre y felicidad baje a 0
        if self.__hunger < 0:
            self.__hunger = 0
        if self.__happy < 0:
            self.__happy = 0

        # Reduce la vida en 1 cada segundo que tiene hambre
        if self.__hunger == 0:
            self.__health -= 1

    def alimentar(self):
        hambre = self.__hunger + 10
        if hambre > Mascota.MAX_HUNGER:
            self.__hunger = Mascota.MAX_HUNGER
        else:
            self.__hunger = hambre


    def jugar(self):
        felicidad = self.__happy + 10
        if felicidad > Mascota.MAX_HAPPY:
            self.__happy = Mascota.MAX_HAPPY
        else:
            self.__happy = felicidad


# Zona de Pruebas
nombre = str(input("Introduzca el nombre de su mascota: "))
print(f"{nombre}, bienvenido al mundo...")

m = Mascota(nombre)

while m.vivo:
    print(m)
    m.actualizar()
    time.sleep(2)

