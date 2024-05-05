
from cazador_del_delta import render_template,get_current_time,json_to_html_table,write_json_config,set_local_time,read_json_config_programas, read_json_config_programa_manual

from machine import Timer, Pin
import time, onewire, ds18x20
import gc
import globales
from globales import read_json_config

class ChangeStateError(Exception):
    pass


# Function to toggle the specified port
def toggle_port(R_pin):
        from machine import Pin
        pin = Pin(R_pin, Pin.OUT)
        pin.value(not pin.value())



# 0 = domingo, 6 = sabado
def rtc_weekday(now):

    MONTH_TABLE = [999, 0, 3, 3, 6, 1, 4, 6, 2, 5, 0, 3, 5 ]
    CENTURY_TABLE = [0, 5, 3, 1, 0 ]
    
    y_2d = now["date"][0] % 100 
    century_index = int((now["date"][0] - y_2d )/ 100 ) % 4


    one = ( now["date"][2] + MONTH_TABLE[now["date"][1]] ) % 7
    two = y_2d % 28 + int((y_2d - (y_2d % 4))/4) + CENTURY_TABLE[century_index] 
    if now["date"][1] <= 2:
        if y_2d % 4 == 0:
            two -= 1
    
    three = (one + two - 1) % 7
    
    return three




    return 1

def rtc_current_time(tz):

    date_time = get_current_time(timezone=tz)

    ret_date = date_time.split(" ")[0]
    ret_time = date_time.split(" ")[1]

    ret_val =  { "time" : [int(ret_time.split(":")[0]), int(ret_time.split(":")[1]), int(ret_time.split(":")[2])], "date" : [int(ret_date.split("-")[0]), int(ret_date.split("-")[1]), int(ret_date.split("-")[2])] }
    #print(f"rtc_current_time: {ret_val} {date_time}")

    return ret_val

def init_pins(Rele_pins):
    
        for i in Rele_pins:
            pin = Pin(i, Pin.OUT)
            pin.value(1)

# funcion para monitorear la carga de la bateria
def battery_charge():
    from machine import ADC
    adc = ADC(Pin(34))
    adc.atten(ADC.ATTN_11DB)
    val = adc.read_uv()* (1.5+0.51)/1.5 #divisor resistivo del rtc
    return val

# in order to sleep inside the function. i request a ticker.
# which is secods. if the ticker is multiple of 10. i read the temp
# if the ticker is odd (impar) and ticker - 1 multimple of 10. i return
# the result
# when reading. returns the list of devices it is reading from.
def temperature_read(ds_sensor, roms, ticker):

    if ticker % 10 == 0:
        try: 
            ds_sensor.convert_temp()
        except:
            return 
        
    if (ticker - 1) % 10 == 0:
        #time.sleep_ms(750)
        ret_val = []
        for rom in roms:
            try:
                ret_val.append(ds_sensor.read_temp(rom))
            except:
                print(f"ERR: falied to read {rom}")
        return ret_val
    

"""
Class Programa ejecuta el timer que realiza la función 
de riego automático.
se accede a través de su funcion self.state()
la que define o modifica su comportamiento.
depende fuertemente de cazador_del_delta.py que administra
la interfaz con el usuario (web server).
"""


class Programa:



    def __init__(self, Rele_pins):

        self.reset_marker = ""
        self.seconds = 0
        self.rele_pins = Rele_pins
        self.states = ["reset","manual_run", "run", "wait", "cancelled", "suspend", "off", "pause", "unpause"]
        self.st = ""
        self.prev_st = ""
        self.counter = 1
        self.delay_secs = [0, 0, 0, 0, 0, 0, 0, 0]
        self.tim=Timer(0)
        self.temp = 0.0 #temperatura del ds18b20
        self.actual_program = ""

        """ variables que tengo que guardar en disco cuando las modifico"""
        self.suspendido_hasta_str = ""
        self.programas_habilitados = [False, False, False]  #""" True cuando puedo correr este programa """
        self.programas_next_time = {"programa_1" : [ 0, 0 ], "programa_2" : [ 0, 0 ], "programa_3" : [0, 0 ]}
        self.dias_de_riego = [ False, False, False, False, False, False, False ] #""" True cuando el dia es de riego. 0 = Domingo """
        self.minutos_riego = [[0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0]] #""" el primer valor no se usa. """
        self.cantidad_de_zonas = 5 #""" cantidad de zonas presentes """
        self.timezone = -3 #""" timezone """



        init_pins(Rele_pins)

        pulse = Pin(2, Pin.OUT)
        pulse.value(0)

        # read riego_suspendido.json
        self.update_suspendido_hasta()
        try:
            #actualiza dias de riego habilitados y tiempos de arranque de cada programa
            self.update_riego_automatico()
        except Exception as e:
            print("Failed to update_riego_automatico():",e)
        # read seteo_programas.json
        try:
            # actualizo los minutos
            self.update_seteo_programas()
        except:
            #valore default ya existen
            pass


        ds_pin = Pin(4)
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        self.roms = self.ds_sensor.scan()
        print('Found DS devices: ', self.roms)

    def update_suspendido_hasta(self):
        try:
            riego_suspendido= read_json_config("riego_suspendido.json")
            print("RIEGO_SUSPENDIDO = ",riego_suspendido)
            self.suspendido_hasta_str = riego_suspendido["suspendido_hasta"][0]
        except:
            self.suspendido_hasta_str = ""
        if self.suspendido_hasta_str <= get_current_time(timezone=self.timezone): # el riego NO esta suspendido
            self.st = "wait"
            self.prev_st = "off"
        else:
            self.st = "suspend"
            self.prev_st = "wait"
        # read riego_automatico.json


    def update_seteo_programas(self):

            seteo_programas = read_json_config("seteo_programas.json")
            print("SETEO_PROGRAMAS = ",seteo_programas)

            for pr in range(1,4,1):
                for zn in range(1,self.cantidad_de_zonas+1,1):
                    try:
                        self.minutos_riego[pr-1][zn] = int(seteo_programas[f"p{pr}-zone{zn}-minutes"][0])
                    except KeyError:
                        self.minutos_riego[pr-1][zn] = 0

                for zn in range(self.cantidad_de_zonas+1,8,1):
                        self.minutos_riego[pr-1][zn] = 0

            print("self.minutos_riego = ",self.minutos_riego)


    def update_riego_automatico(self):
            riego_automatico = read_json_config("riego_automatico.json")
            print("RIEGO_AUTOMATICO = ",riego_automatico)
            
            self.dias_de_riego = [ False, False, False, False, False, False, False ] #""" True cuando el dia es de riego. 0 = Domingo """
            SEMANA = ["domingo", "lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
            for key in SEMANA:
                try:
                    #print(f"DIA = {key} \nRIEGO_AUTOMATICO = {riego_automatico[key][0]}")
                    if riego_automatico[key][0] == "on":
                        self.dias_de_riego[SEMANA.index(key)] = True
                except KeyError:
                    pass
            for pr in ["programa_1","programa_2","programa_3"]:
                    try:
                        self.programas_next_time[pr][0] = int(riego_automatico[pr+"_start_hour"][0])
                        self.programas_next_time[pr][1] = int(riego_automatico[pr+"_start_minute"][0])
                    except KeyError:
                        self.programas_next_time[pr][0] = 0
                        self.programas_next_time[pr][1] = 0


            print("update_riego_automatico(): self.dias_de_riego = ",self.dias_de_riego)
            print("update_riego_automatico(): self.programas_next_time = ",self.programas_next_time)
            return

    def dia_de_riego(self, time):

        wday = rtc_weekday(time)
        return self.dias_de_riego[wday]



# Possible states for the state machine:
# wait: program is waiting for a calendar alarm.
#       the program checks the time and runs if the time matches 
#       the start time of a given program.
#       it sets the staet to run and loads the delay_secs variable.
# manual_run: this state is entered from run_program.
#             it sets the delay secs when called and then 
#             under this state we start the program instead of
#             doing it from the wait state
# run:  the program is running a watering cycle.
#       it decrements delay_secs 1 sec at a time from each station
#       until it reaches 0 on all stations. then it powers off the
#       relay 0 (PUMP) and state changes to "wait"
# off:  no program can run
# pause: stops the timer functions. its a state which immediately returns
#        to the running application. Go back to the previous state with
#        programa.state("unpause"). It is not allowed to change the
#        state when paused unless it is "unpause"
#
#  cancelled: this state is used when you wish to cancel a running
#             program. it forces the relays to off status and
#             switches to the previous state before the program
#             started
#
# the function usage is to change the behaviour of the staet machine
# if you manually set state(run, [ 0, m1 .. m7 ] where m1-m7 are
# numbers which represente the time to run each zone.
# it is treated as a manual run. later it will return
# to the previous state (either off or wait in normal conditions)
###
    def state(self, new_state=None, new_delay_secs=None):

        if new_state is None:
            return self.st
        if new_state == "unpause":
            if self.st == "pause":
                self.st = self.prev_st
            return self.st
                
        if new_state == "reset":
            self.st = new_state
            self.reset_marker = rtc_current_time(self.timezone)
            self.reset_marker["time"][2] += 10
            if self.reset_marker["time"][2] > 59:
                self.reset_marker["time"][2] -= 60
                self.reset_marker["time"][1] += 1
                if self.reset_marker["time"][1] > 59:
                    self.reset_marker["time"][1] -= 60
                    self.reset_marker["time"][0] += 1
                    if self.reset_marker["time"][0] > 23:
                        self.reset_marker["time"][0] -= 24
                        self.reset_marker["date"][2] += 1


            return

        try:
            if self.st == "pause":
                if new_state != "unpause":
                    raise ChangeStateError("Cannot switch from pause state without unpausing first")

            if new_state == "cancelled":
                if self.st != "run":
                    raise ChangeStateError("Can only change from run state to cancelled") 

            self.prev_st = self.st
            self.st = new_state
            if new_delay_secs is not None:
                self.delay_secs = new_delay_secs
                # clobber seconds for zones not present.
                for i in range(len(self.delay_secs)):
                    if i + 1 > self.cantidad_de_zonas:
                        self.delay_secs[i] = 0 
            
        except ValueError:
            print("programa.state new_state not valid:",new_state)
            return self.st
        except ChangeStateError:
            return self.st
        return self.st

    def run_program(self, program_name = None):
        
        if self.state() == "run" or self.state() == "manual_run":
            #print("WARN: run_program cannot execute if running already. cancel program first.")
            return [self.actual_program, sum(self.delay_secs)]

        elif not program_name:
            return None

        # need to check if program_name exists.
        delay_mins = self.minutos_riego[int(program_name.split("_")[1]) -1]
        self.delay_secs = [x * 60 for x in delay_mins]
        self.actual_program = program_name

        #special case, run a program that has 0 minutes to run.
        # need to skip this run.
        if sum(self.delay_secs) != 0:
            self.state("manual_run")


    def state_machine(self):
        now_time = rtc_current_time(self.timezone)

        if self.state() == "reset":
            from machine import reset
            print(f"now = {now_time}")
            print(f"reset = {self.reset_marker}")
            if now_time["time"] > self.reset_marker["time"]:
               reset()


        if self.state() == "pause":
            return



        if self.state() == "off":
            return;
        
        if self.state() == "manual_run":
            print(f"Starting manual program." )
            print(self.delay_secs)
            toggle_port(self.rele_pins[0])
            toggle_port(2) # invert the operation of the pulse for timer.
            self.state("run")

        if self.state() == "wait":

            if self.dia_de_riego(now_time):


                for program in self.programas_next_time:
                    if self.programas_next_time[program] == [now_time["time"][0], now_time["time"][1]]:
                        if now_time["time"][2] < 2:
                            delay_mins = self.minutos_riego[int(program.split("_")[1]) - 1]
                            self.delay_secs = [x * 60 for x in delay_mins]

                            #special case, run a program that has 0 minutes to run.
                            # need to skip this run.
                            if sum(self.delay_secs) != 0:
                                print(f'Starting program: {program} at {now_time["time"][0]}:{now_time["time"][1]}' )
                                self.actual_program = program
                                print(self.delay_secs)

                                toggle_port(self.rele_pins[0])
                                toggle_port(2) # invert the operation of the pulse for timer.
                                self.state("run")

            #else:
            #    print("No es un dia de riego habilitado!!")


        if(self.state() == "cancelled"):
            print("Riego Cancelado")
            init_pins(self.rele_pins)
            self.counter = 1
            self.state("wait")
            toggle_port(2) # invert the operation of the pulse for timer.

        if(self.state() == "run"):       
            pin = Pin(self.rele_pins[self.counter], Pin.OUT)
            while self.delay_secs[self.counter] ==  0:                                                                          
                if not pin.value():
                    toggle_port(self.rele_pins[self.counter])
                    
                self.counter += 1
                if self.counter == self.cantidad_de_zonas + 1:
                    self.counter = 1
                    self.state("wait")
                    toggle_port(self.rele_pins[0])
                    toggle_port(2) # invert the operation of the pulse for timer.
                    return

            if pin.value():
                toggle_port(self.rele_pins[self.counter])
                print("Encendiendo rele", self.counter, "por", self.delay_secs[self.counter], "segundos")
            self.delay_secs[self.counter] = self.delay_secs[self.counter] - 1
        
        if self.state() == "suspend":
            #print("programa_riego suspendido_hasta_str:",suspendido_hasta_str)
            if self.suspendido_hasta_str <= get_current_time(timezone=self.timezone): # el riego NO esta suspendido
                self.state("wait")
#            else:
#                print(f"Riego suspendido hasta: {suspendido_hasta_str}")

    # returns status of running program.
    # tuple [ "programa", minutes remaining, zone number ]
    # returns None if it is not running
    # TODO: now it has first value hardcoded.
    #       need to see how it is best to get this info.

    def program_running(self):
        ret_val = None
        if self.state() == "run":
            ret_val = []
            ret_val.append(f"{self.actual_program}")
            ret_val.append(sum(self.delay_secs))
            ret_val.append(self.counter)

        return ret_val

    def interrupt_func(self, t):
        toggle_port(2)
        if self.seconds == 60:
            self.seconds = 0

        #if self.seconds == 0:
        #    b_level = battery_charge()/1000000
        #    print(f"Battery level: {b_level:1.2f}V")
        self.state_machine()

        #temps = temperature_read(self.ds_sensor, self.roms, self.seconds)
        #try:
        #    for temp in temps:
        #        if isinstance(temp, float):
        #            self.temp = temp
        #           # print(f"Temperature: {temp:2.2f} C")
        #except TypeError:
        #    pass
        self.seconds += 1
        gc.collect()
        free_mem = gc.mem_free()
        #if free_mem < 50000:
        print(f"program runnning: {self.program_running()}, Free ram: {free_mem}                         ", end = '\r')
        
        toggle_port(2)

   # starts the timer for the programs.
    def run(self, periodo):

        self.tim.init(mode=Timer.PERIODIC, period=periodo, callback=self.interrupt_func)




