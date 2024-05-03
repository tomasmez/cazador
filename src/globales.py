import gc
import ujson

gc.enable()
def read_json_config(file_path):

    try:
        with open(file_path, 'r') as file:
            json_data_local = ujson.load(file)
            return json_data_local
    except Exception as e:
        print('Error',e)
        return {}

def init():
    global riego_automatico
    global riego_suspendido
    global seteo_programas

    # huso horario. default -3
    global timezone
    # cuantas zonas reales tiene conectadas el equipo. default 7
    global cantidad_de_zonas


    try:
        riego_automatico = read_json_config("riego_automatico.json")
    except:
        riego_automatico = {}
    try:
        riego_suspendido = read_json_config("riego_suspendido.json")
    except:
        riego_suspendido = {}
    try:
        seteo_programas = read_json_config("seteo_programas.json")
    except:
        seteo_programas = {}

    try:
        configuracion = read_json_config("configuracion.json")
        cantidad_de_zonas = configuracion["cantidad_de_zonas"]
        timezone = configuracion["timezone"]
    except:
        cantidad_de_zonas = 5
        timezone = -3



def print_g(g_var = None):
    if not g_var:
        return globals()
    return globals()[g_var]
