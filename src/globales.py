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



def print_g(g_var = None):
    if not g_var:
        return globals()
    return globals()[g_var]
