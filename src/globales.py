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
    global riego_cancelado
    global seteo_programas

    try:
        riego_automatico = read_json_config("riego_automatico.json")
    except:
        riego_automatico = {}
    try:
        riego_cancelado = read_json_config("riego_cancelado.json")
    except:
        riego_cancelado = {}
    try:
        seteo_programas = read_json_config("seteo_programas.json")
    except:
        seteo_programas = {}



