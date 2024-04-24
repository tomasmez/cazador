import sys
import gc

gc.enable()


from microdot import Microdot, Response, send_file,redirect
from cazador_del_delta import render_template,get_current_time,json_to_html_table,read_json_config,read_json_config_programas,write_json_config,set_local_time,read_json_config_programa_automatico,read_json_config_programa_manual,transform_seteo_programas_json
#from calculate_sunrise_sunset import get_sunrise_sunset_times
from programa_riego import Programa, toggle_port


sys.path.append('microdot')


app = Microdot()
Response.default_content_type = 'text/html'

reles=[23, 5, 14, 27, 16, 17, 25, 26]
p1=Programa(reles)
p1.run(1000)

@app.route('/', methods=['GET', 'POST'])
async def index(request):
    template = 'templates/index.html'
    my_dict = { }
    my_dict["hora_actual"] = get_current_time()
    riego_automatico_json = read_json_config_programa_manual("riego_automatico.json")
    print('---riego_automatico_json---')
    print(riego_automatico_json)
    print('----')
    #my_dict["riego_programado"] = json_to_html_table(riego_automatico_json)
    seteo_programas_json = read_json_config_programas("seteo_programas.json")
    print('---seteo_programas_json---')
    print(seteo_programas_json)
    print('----')
    seteo_programas_json_transformed = transform_seteo_programas_json(seteo_programas_json,riego_automatico_json)
    print('---seteo_programas_transformed---')
    print(seteo_programas_json)
    print('----')   
    
    my_dict["programas_configurados"] = json_to_html_table(seteo_programas_json_transformed)
    riego_cancelado_json = read_json_config("riego_cancelado.json")
    print(riego_cancelado_json,type(riego_cancelado_json))
    try:
        cancelado_hasta_str = riego_cancelado_json["cancelado_hasta"][0]
        if cancelado_hasta_str > get_current_time(): # el riego NO esta cancelado
            print('CONFIRMADO Riego cancelado hasta',cancelado_hasta_str)
            my_dict["riego_cancelado"] = f"<mark>{cancelado_hasta_str}</mark>"
        else:
            my_dict["riego_cancelado"] = 'RIEGO ACTIVO'
    except:
        my_dict["riego_cancelado"] = 'RIEGO ACTIVO'
    config = 'riego_cancelado.json'
    if request.method == 'POST':
        hora_actual_str = get_current_time()
        cancelado_hasta_str = get_current_time(int(request.form["dias_cancelados"]))
        if cancelado_hasta_str > hora_actual_str: # se cancela el riego, ponemos algo en rojo para ver
            print('RIEGO CANCELADO hasta:',cancelado_hasta_str)
            #dias_cancelados = f'<p style="color:red;">RIEGO CANCELADO POR {request.form["dias_cancelados"]} dias</p>'
            #request.form["dias_cancelados"] = dias_cancelados
        request.form["cancelado_hasta"] = cancelado_hasta_str
        p1.state("pause")
        write_json_config(config,request.form)
        p1.state("unpause")
        return redirect('/')
    else:
        return render_template(template,my_dict)
    
"""    
@app.route('/cancelar_riego', methods=['GET', 'POST'])
async def cancelar_riego(request):
    template = 'templates/cancelar_riego.html'
    config = 'riego_cancelado.json'
    if request.method == 'POST':
        hora_actual_str = get_current_time()
        cancelado_hasta_str = get_current_time(int(request.form["dias_cancelados"]))
        if cancelado_hasta_str > hora_actual_str: # se cancela el riego, ponemos algo en rojo para ver
            print('RIEGO CANCELADO hasta:',cancelado_hasta_str)
            #dias_cancelados = f'<p style="color:red;">RIEGO CANCELADO POR {request.form["dias_cancelados"]} dias</p>'
            #request.form["dias_cancelados"] = dias_cancelados
        request.form["cancelado_hasta"] = cancelado_hasta_str
        p1.state("pause")
        write_json_config(config,request.form)
        p1.state("unpause")
        return redirect('/')
    else:
        return render_template(template)
"""
    
@app.route('/config', methods=['GET', 'POST'])
async def seteo_hora(request):
    template = 'templates/config.html'

    if request.method == 'POST':
        post_time_str = request.form["datetime"]
        #print('-->',type(post_time_str),post_time_str)
        try:
            set_local_time(post_time_str)
        except Exception as ex:
            print(f'Error guardando hora post:{ex}')
        return redirect('/')    
    else:
        return send_file(template)

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
        request.form["hora_update"] = get_current_time()
        p1.state("pause")
        write_json_config(config,request.form)
        p1.state("unpause")
        return redirect('/')
    else:
        return send_file(template)
    
@app.route('/seteo_riego_manual', methods=['GET', 'POST'])
async def seteo_riego_manual(request):
    template = 'templates/seteo_riego_manual.html'
    config = 'riego_manual.json'
    if request.method == 'POST':
        request.form["hora_update"] = get_current_time()
        p1.state("pause")
        write_json_config(config,request.form)
        p1.state("unpause")
        return redirect('/')
    else:
        return send_file(template) 
        

@app.route('/tiempos_riego', methods=['GET', 'POST'])
async def seteo_programas(request):
    template = 'templates/tiempos_riego.html'
    config = 'seteo_programas.json'
    if request.method == 'POST':
        request.form["hora_update"] = get_current_time()
        p1.state("pause")
        write_json_config(config,request.form)
        p1.state("unpause")
        return redirect('/')
    else:
        return send_file(template) 
        
@app.route('/prueba_zonas', methods=['GET', 'POST'])
async def prueba_zonas(request):
    
    # Function to toggle the specified port
    def toggle_port(port):
        from machine import Pin
        pin = Pin(int(port), Pin.OUT)
        pin.value(not pin.value())

    
    template = 'templates/prueba_zonas.html'
    config = 'prueba_zonas.json'
    if request.method == 'POST':
        port = request.form["port"] 
        print(f"Toggling port: {port}")
        toggle_port(int(port))
        return redirect('/prueba_zonas')
    else:
        return send_file(template) 


print('Server started')
app.run(port=80,debug=True)
