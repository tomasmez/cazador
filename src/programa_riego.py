
from cazador_del_delta import render_template,get_current_time,json_to_html_table,read_json_config,write_json_config,set_local_time,read_json_config_programas, read_json_config_programa_manual

from machine import Timer, Pin
import time, onewire, ds18x20
import gc

class ChangeStateError(Exception):
    pass


# Function to toggle the specified port
def toggle_port(R_pin):
        from machine import Pin
        pin = Pin(R_pin, Pin.OUT)
        pin.value(not pin.value())

def read_minutes(programa="programa_1"):

        s_pr = read_json_config_programas("seteo_programas.json")
        
        p_n = programa.split("_")[1]

        delay_mins = [ 0,
                           int(s_pr[f"p{p_n}-zone1-minutes"][0]),
                           int(s_pr[f"p{p_n}-zone2-minutes"][0]),
                           int(s_pr[f"p{p_n}-zone3-minutes"][0]),
                           int(s_pr[f"p{p_n}-zone4-minutes"][0]),
                           int(s_pr[f"p{p_n}-zone5-minutes"][0]),
                           int(s_pr[f"p{p_n}-zone6-minutes"][0]),
                           int(s_pr[f"p{p_n}-zone7-minutes"][0]) ]

        # print(delay_mins)

        return delay_mins

def programa_get_next_time():
    
    jdata = read_json_config_programa_manual("riego_automatico.json")
    #print(jdata)

    ret_data = {}

    for pr in [ "programa_1", "programa_2", "programa_3" ]:
        try:
            ret_data.update({ pr : [int(jdata[pr]["hora"]),int(jdata[pr]["minuto"])] } )
    
        except KeyError:
            pass
    return ret_data


def rtc_current_time():
    from machine import I2C, Pin
    from ds1307 import DS1307

                # Get the current time in seconds since the epoch
    I2C_ADDR = 0x68  # DEC 104, HEX 0x68
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
    ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)

    # Get the current RTC time as a tuple (year, month, day, hour, minute, second, weekday, yearday)
    ret_val =  { "time" : [ds1307.hour, ds1307.minute, ds1307.second], "date" : [ds1307.year, ds1307.month, ds1307.day] }

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
        self.states = ["reset", "run", "wait", "cancelled", "suspend", "off", "pause", "unpause"]
        self.st = "wait"
        self.prev_st = "off"
        self.counter = 1
        self.delay_secs = [0, 1, 3, 0, 10, 5, 1, 1]
        self.tim=Timer(0)

        init_pins(Rele_pins)

        ds_pin = Pin(4)
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        self.roms = self.ds_sensor.scan()
        print('Found DS devices: ', self.roms)

# Possible states for the state machine:
# wait: program is waiting for a calendar alarm.
#       the program checks the time and runs if the time matches 
#       the start time of a given program.
#       it sets the staet to run and loads the delay_secs variable.
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
            self.reset_marker = rtc_current_time()
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
            index=self.states.index(new_state)
            if self.st == "pause":
                if new_state != "unpause":
                    raise ChangeStateError("Cannot switch from pause state without unpausing first")

            # if we are un run and wish to cancel. we cancel:
            #            1. init pins 
            #            2. new state index = index of prev_st
            #            3. prev state = "run"
            if new_state == "cancelled":
                if self.st != "run":
                    raise ChangeStateError("Can only change from run state to cancelled") 
                init_pins(self.rele_pins)
                self.counter = 1
                index=self.states.index(self.prev_st)

            self.prev_st = self.st
            self.st = self.states[index]
            if new_delay_secs is not None:
                if len(new_delay_secs) == 8:
                    self.delay_secs = new_delay_secs
            
        except ValueError:
            print("programa.state new_state not valid:",new_state)
            return self.st
        except ChangeStateError:
            return self.st
        return self.st



    def state_machine(self):
        now_time = rtc_current_time()

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


        if self.state() == "wait":
            next_time = programa_get_next_time()

            for program in next_time:
                if next_time[program] == [now_time["time"][0], now_time["time"][1]]:
                    if now_time["time"][2] < 2:
                        delay_mins = read_minutes(program)
                        self.delay_secs = [x * 60 for x in delay_mins]

                        #special case, run a program that has 0 minutes to run.
                        # need to skip this run.
                        if sum(self.delay_secs) != 0:
                            print(f"Starting program: {program} at {now_time["time"][0]}:{now_time["time"][1]}" )
                            print(self.delay_secs)

                            toggle_port(self.rele_pins[0])
                            self.state("run")


        if(self.state() == "cancelled"):
           print("Riego Cancelado")
           init_pins(self.rele_pins)
           self.state(self.prev_st)

        if(self.state() == "run"):       
            pin = Pin(self.rele_pins[self.counter], Pin.OUT)
            while self.delay_secs[self.counter] ==  0:                                                                          
                if not pin.value():
                    toggle_port(self.rele_pins[self.counter])
                    
                self.counter += 1
                if self.counter == 8:
                    self.counter = 1
                    self.state(self.prev_st)
                    toggle_port(self.rele_pins[0])
                    return

            if pin.value():
                toggle_port(self.rele_pins[self.counter])
                print("Encendiendo rele", self.counter, "por", self.delay_secs[self.counter], "segundos")
            self.delay_secs[self.counter] = self.delay_secs[self.counter] - 1
        
        if self.state() == "suspend":
            riego_cancelado_json = read_json_config("riego_cancelado.json")
            cancelado_hasta_str = riego_cancelado_json["cancelado_hasta"][0]
            if cancelado_hasta_str > get_current_time(): # el riego NO esta cancelado
                self.state(self.prev_st)
            else:
                print(f"Riego suspendido hasta: {cancelado_hasta_str}")

    # returns status of running program.
    # tuple [ "programa", minutes remaining, zone number ]
    # returns None if it is not running
    def program_running(self):
        ret_val = None
        if self.state() == "run":
            ret_val = []
            ret_val.append("programa")
            ret_val.append(sum(self.delay_secs))
            ret_val.append(self.counter)

        return ret_val

    def interrupt_func(self, t):
        pulse = Pin(2, Pin.OUT)
        pulse.value(1)
        if self.seconds == 60:
            self.seconds = 0

        if self.seconds == 0:
            b_level = battery_charge()/1000000
            print(f"Battery level: {b_level:1.2f}V")
        self.state_machine()

        temps = temperature_read(self.ds_sensor, self.roms, self.seconds)
        try:
            for temp in temps:
                if isinstance(temp, float):
                    print(f"Temperature: {temp:2.2f} C")
        except TypeError:
            pass
        self.seconds += 1
        gc.collect()
        #print(f"program runnning: {self.program_running()}, Free ram: {gc.mem_free()}")
        
        pulse.value(0)

   # starts the timer for the programs.
    def run(self, periodo):

        self.tim.init(mode=Timer.PERIODIC, period=periodo, callback=self.interrupt_func)




