from machine import RTC
import sys
import gc
import os,network
import ujson
import asyncio

gc.enable()

from microdot import Microdot, Response, send_file,redirect
from cazador_del_delta import render_template,get_current_time,json_to_html_table,read_json_config_programas,write_json_config,set_local_time,read_json_config_programa_manual,transform_seteo_programas_json
from cazador_del_delta import read_calendario,check_wifi, read_json_config,test_wifi_connection, write_wifi_credentials_to_file
#from calculate_sunrise_sunset import get_sunrise_sunset_times
from programa_riego import Programa, toggle_port, init_pins
from machine import RTC

def ceiling(x):
    n = int(x)
    return n if n-1 < x <= n else n+1

rtc = RTC()

print(f"RTC time: {rtc.datetime()}")


sys.path.append('microdot')


app = Microdot()
Response.default_content_type = 'text/html'

reles=[23, 5, 14, 27, 16, 17, 25, 26]
p1=Programa(reles)
p1.run(1000)

@app.route('/', methods=['GET', 'POST'])
def index(request):
    gc.collect()
    print("entering /...")
    if request.method == 'POST':
        hora_actual_str = get_current_time(timezone=p1.timezone)
        try:
            suspendido_hasta_str = get_current_time(p1.timezone, int(request.form["dias_suspendidos"]))
            if suspendido_hasta_str > hora_actual_str: # se cancela el riego, ponemos algo en rojo para ver
                print('RIEGO SUSPENDIDO hasta:',suspendido_hasta_str)
                #dias_suspendidos = f'<p style="color:red;">RIEGO CANCELADO POR {request.form["dias_suspendidos"]} dias</p>'
                #request.form["dias_suspendidos"] = dias_suspendidos
            request.form["suspendido_hasta"] = suspendido_hasta_str
            p1.state("pause")
            config = 'riego_suspendido.json'
            write_json_config(config,request.form)
            p1.update_suspendido_hasta()
            p1.state("unpause")
            return redirect('/')
        except Exception as ex:
            print("hubo una excepcion dentro de dias suspendidos:", ex)
            pass
        try:
            programa_manual = request.form["programa_manual"]
                
            print(f"Corriendo programa manual: {programa_manual}")    
            p1.run_program(programa_manual)
        except:
            pass
        try:
            riego_cancelado = request.form["cancelar"]
            print(f"Cancelando programa actual: {riego_cancelado}")    
            p1.state("cancelled")
        except:
            pass
    # main route , redirected if json are missing
    if p1.state() == "run" or p1.state() == "manual_run":
        template = 'templates/index_running.html'
    else:
        template = 'templates/index_not_running.html'

    my_dict = { }
    my_dict["hora_actual"] = get_current_time(timezone=p1.timezone)
    riego_automatico_json = read_json_config_programa_manual("riego_automatico.json")
#    print('---riego_automatico_json---')
#    print(riego_automatico_json)
#    print('----')
    #my_dict["riego_programado"] = json_to_html_table(riego_automatico_json)
    seteo_programas_json = read_json_config_programas("seteo_programas.json")
#    print('---seteo_programas_json---')
#    print(seteo_programas_json)
#    print('----')
    seteo_programas_json_transformed = transform_seteo_programas_json(seteo_programas_json,riego_automatico_json)
#    print('---seteo_programas_transformed---')
#    print(seteo_programas_json)
#    print('----')   
    calendario_json = read_calendario("riego_automatico.json")
#    print('---seteo_programas_transformed---')
#    print(calendario_json)
#    print('----')      

    try:
        seteo_programas_json_transformed["dias_habilitados"] = calendario_json["dias_habilitados"]
    except:
        pass
    
    my_dict["programas_configurados"] = json_to_html_table(seteo_programas_json_transformed)
    try:
        if p1.suspendido_hasta_str > get_current_time(timezone=p1.timezone): # el riego NO esta suspendido
            print('CONFIRMADO Riego suspendido hasta',p1.suspendido_hasta_str)
            my_dict["riego_suspendido"] = f"<mark>{p1.suspendido_hasta_str}</mark>"
        else:
            print('Riego activo fecha vieja:',p1.suspendido_hasta_str)
            my_dict["riego_suspendido"] = 'RIEGO ACTIVO'
    except:
        my_dict["riego_suspendido"] = 'RIEGO ACTIVO'
    try:
        my_dict["running_program_nr"] = p1.run_program()[0]
        my_dict["running_program_min"] = ceiling(p1.run_program()[1]/60)
    except:
        pass
    gc.collect()
    return render_template(template,my_dict)
    

# Endpoint to call the function
@app.route('/call_function')
def call_function(request):
    function_name = request.args.get('function_name')
    if function_name:
        # Check if the function exists in the globals
        if function_name in globals() and callable(globals()[function_name]):
            # Call the function dynamically
            result = globals()[function_name]()
            return {"result": result}
        else:
            return {"error": "Function not found"}, 404
    else:
        return {"error": "Function name not provided"}, 400


@app.route('/config', methods=['GET', 'POST'])
async def seteo_hora(request):
    rtc = RTC()
    rtc.memory('')
    current_time = get_current_time(timezone=p1.timezone)
    print("CONFIG: Current time is:",current_time)

    template = 'templates/config.html'
    #if p1.state() == "run":
    #    print("tratando de cancelar")
    #    p1.state("cancelled")
    #else:
    #    p1.run_program("program_1")

    if request.method == 'POST':
        try:
            post_time_str = request.form["datetime"]
            #print('-->',type(post_time_str),post_time_str)
            set_local_time(post_time_str)
        except Exception as ex:
            pass
            #print(f'Error guardando hora post:{ex}')
        try:
            cant_zonas = request.form["cant_zonas"]

            if p1.state() == "run":
                init_pins(reles)
                p1.state("wait")

            p1.cantidad_de_zonas = int(cant_zonas)
            print(f"cantidad de zonas actualzada: {p1.cantidad_de_zonas}")
            write_json_config("config.json",request.form)
        except:
            pass
        return redirect('/')    
    else:
        # fill in current time automatically
        my_dict = {"auswahl1":"","auswahl2":"","auswahl3":"","auswahl4":"","auswahl5":"","auswahl6":"","auswahl7":""}
        my_dict["auswahl"+str(p1.cantidad_de_zonas)] = 'selected="selected"'
        my_dict["current_time"] = current_time
        return render_template(template,my_dict)

@app.route('/hard_reset',)
async def hard_reset(request):
    p1.state("reset")
    return redirect('/')    
#    from machine import reset
#    reset()

@app.route('/horas_arranque', methods=['GET', 'POST'])
async def horas_arranque(request):
    template = 'templates/horas_arranque.html'
    config = 'riego_automatico.json'
    
    if request.method == 'POST':
        request.form["hora_update"] = get_current_time(timezone=p1.timezone)
        p1.state("pause")
        print("hora_arranque: ",request.form)
        write_json_config(config,request.form)
        p1.update_riego_automatico()
        p1.state("unpause")
        return redirect('/')
    else:
        return send_file(template)
        
@app.route('/horas_arranque_json', methods=['GET'])
async def horas_arranque_json(request):
    riego_automatico_json = read_json_config_programa_manual("riego_automatico.json")
    return riego_automatico_json
        

@app.route('/tiempos_riego', methods=['GET', 'POST'])
async def seteo_programas(request):
    gc.collect()
    template = 'templates/tiempos_riego.html'
    config = 'seteo_programas.json'
    if request.method == 'POST':
        request.form["hora_update"] = get_current_time(timezone=p1.timezone)
        p1.state("pause")
        write_json_config(config,request.form)
        p1.update_seteo_programas()
        p1.state("unpause")
        return redirect('/')
    else:
        my_dict= {}
        for pr in range(1,4,1):
            for i in range(1, p1.cantidad_de_zonas + 1,1):
                my_dict[f"P{pr}Z{i}"] = f'    <div>\n      <label for="p{pr}-zone{i}">Zona {i}</label>\n      <label for="p{pr}-zone{i}-minutes">Minutos:</label>\n      <select id="p{pr}-zone{i}-minutes" name="p{pr}-zone{i}-minutes">\n      <option value=""></option>\n    </select>\n    </div>'
            for i in range(p1.cantidad_de_zonas + 1,8,1):
                my_dict[f"P{pr}Z{i}"] = ' '
        my_dict["CANT_ZONAS"] = f"{p1.cantidad_de_zonas}"

        gc.collect()
        return render_template(template,my_dict) 
        


@app.route('/return_json_file')
def return_json_file(request):
    # used to retrive existing config from js
    # Get the file name from the query parameter
    file_name = request.args.get('file')

    # Check if the file name is provided
    if not file_name:
        return ujson.load({'error': 'File name not provided'})

    try:
        json_data = read_json_config(file_name)
        #print(json_data)
        #print(read_json_config(file_name))
    except:
        pass
    return json_data


# Route to handle registration
@app.route('/registration', methods=['GET', 'POST'])
def register(request):
    print('Registration endpoint')
    template = 'templates/registration.html'
    my_dict = {}
    if request.method == 'POST':
        device_name = request.form['device_name']
        wifi_connected, ip = check_wifi()
        print('POST received and wifi is :',wifi_connected,ip)
        if wifi_connected:
            url = f"http://chat2023.pythonanywhere.com/register?device_name={device_name}&device_ip={ip}&device_id=test"
            print(url)
            response = urequests.get(url)
            if response.status_code == 200:
                # Save device name to registered.json
                with open('registered.json', 'w') as f:
                    ujson.dump({'device_name': device_name}, f)
                my_dict["device_name"] = device_name
                return render_template(template,my_dict)
            else:
                my_dict["device_name"] = 'FAILED_TO_REGISTER'
                return render_template(template,my_dict)
        else:
                my_dict["device_name"] = 'WIFI_NOT_CONNECTED'
                return render_template(template,my_dict)
    elif request.method == 'GET':
        try:
            print('Attempting to read registered.json')
            with open('registered.json', 'r') as f:
                data = ujson.load(f)
                device_name = data['device_name']
                my_dict["device_name"] = device_name
            return render_template(template,my_dict)
        except Exception as ex:
            my_dict["device_name"] = 'NO_DEVICE_REGISTERED'
            return render_template(template,my_dict)


# Function to scan WiFi networks and return SSIDs with their signal strengths
def scan_wifi():
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_sta.active()
    print('Wifi client is active.Scanning networks.')
    networks = wlan_sta.scan()
    print('Networks found from scan:',networks)
    return [(network1[0].decode(), network1[3]) for network1 in networks]  # SSID and power

# Flask route to handle WiFi scanning and return SSIDs with signal strengths
@app.route('/scan_wifi', methods=['GET'])
def get_wifi_networks(request):
    try:
        networks = scan_wifi()
        return {'networks': networks}
    except Exception as e:
        return {'error': str(e)}



@app.route('/wifi_config', methods=['GET','POST'])
def wifi_config_menu(request):
    my_dict = {}
    if request.method == 'POST':
        try:
            print(request.form)
            if 'wifiDropdown' in request.form:
                ssid = request.form['wifiDropdown']
            elif 'manualSSID' in request.form:
                ssid = request.form['manualSSID']
            password = request.form["password"]
            print('ssid y pwd rx',ssid,password)
            
            write_wifi_credentials_to_file(ssid,password)
            my_dict["mensaje"] = "Clave guardada."
            return render_template('templates/wifi_config.html',my_dict)
        except Exception as ex:
            my_dict["mensaje"] = ex
            return render_template('templates/wifi_config.html',my_dict)
        
    else: #GET
        try:
            result = request.form["result"]
            my_dict["mensaje"] = result
            return render_template('templates/wifi_config.html',my_dict)
        except:
            my_dict["mensaje"] = "Aqui podra escanear y guardar la config de wifi."
            return render_template('templates/wifi_config.html',my_dict)





print('Server started')
#app.run(port=80,debug=True)
async def starter():
    await app.start_server(port=80,debug=True)

asyncio.run(starter())
