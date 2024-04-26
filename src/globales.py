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

    riego_automatico = read_json_config("riego_automatico.json")
    riego_cancelado = read_json_config("riego_cancelado.json")
    seteo_programas = read_json_config("seteo_programas.json")


