from random import randint
from time import sleep


class Autobus:
    def __init__(self, id):
        self.id = id
        self.clientes = []
        self.posicion = []
        self.parado = False

    def realizar_parada(self, entorno):
        lista_clientes_fuera = []

        for cliente in self.clientes:
            rand = randint(0, 2)
            if rand == 0:
                self.clientes.remove(cliente)
                cliente.pasajero.release()
                entorno.matriz[cliente.posicion[0]][cliente.posicion[1]].clientes.append(cliente)
                lista_clientes_fuera.append(cliente)

        return lista_clientes_fuera

    def obtener_clientes(self):
        res = []
        for cliente in self.clientes:
            res.append(cliente.id)
        return res

    def ciclo_autobus(self, juego):
        primera_iteracion = True
        cont = 0

        while not juego.elemento_ganador:
            cont = cont + 1

            if len(self.clientes) == juego.N_AUTOBUS_GANA:  # estado[4] contiene los clientes del autobus
                juego.elemento_ganador = "AUTOBUS"
                break

            if primera_iteracion:
                primera_iteracion = False
                pos_posibles = [[0, 0], [0, juego.DIMENSION_MATRIZ - 1], [juego.DIMENSION_MATRIZ - 1, 0],
                                [juego.DIMENSION_MATRIZ - 1, juego.DIMENSION_MATRIZ - 1]]
                pos_disp = []
                while not pos_disp:
                    pos_bloqueadas = juego.lock_posiciones(pos_posibles)
                    pos_disp = juego.casillas_sin_vehiculos(pos_bloqueadas, False)
                    if len(pos_disp) == 0:
                        juego.unlock_casillas(pos_bloqueadas)
                        sleep(0.2)
                    else:
                        if len(pos_disp) == 1:
                            juego.insertar_elemento(self, pos_disp[0])
                        else:
                            juego.insertar_elemento(self, pos_disp[randint(0, len(pos_disp) - 1)])
                        juego.imprimir(["Colocacion autobus: ID= ", self.id, "  POS= ", self.posicion, " CLIENTES= ",
                                        self.obtener_clientes(), "cont=", cont])
                        juego.unlock_casillas(pos_bloqueadas)
            else:
                pos_bloqueadas = juego.lock_alrededor(self.posicion)
                pos_disp = juego.casillas_sin_vehiculos(pos_bloqueadas)
                if len(pos_disp) == 1:
                    rand_index = 0
                else:
                    rand_index = randint(0, len(pos_disp) - 1)
                juego.insertar_elemento(self, pos_disp[rand_index])
                if cont % 3 == 0:  # cada 3 mov una parada
                    list_clientes = self.realizar_parada(juego)
                    self.parado = True
                    juego.print_lock.acquire()
                    print("AUTOBUS se mueve y PARA: ID=", self.id, " POS= ", self.posicion, "PASAJEROS= ",
                          self.obtener_clientes(), " cont", cont)
                    for cliente in list_clientes:
                        print("PASAJERO FUERA: ClienteID= ", cliente.id, "  AutobusDejado= ", self.id, "  Posicion= ",
                              cliente.posicion,
                              "  pasajero?: ", cliente.pasajero.locked())
                    juego.print_lock.release()
                    juego.unlock_casillas(pos_bloqueadas)
                    sleep(1.5)
                    self.parado = False
                else:
                    juego.unlock_casillas(pos_bloqueadas)
                    sleep(2)

        for cliente in self.clientes:
            if cliente.pasajero.locked():
                cliente.pasajero.release()
