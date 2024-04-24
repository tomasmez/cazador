import utime
import ujson
from ds1307 import DS1307
from machine import I2C, Pin
from time import gmtime, time

def render_template(filename, values_dict={}):
    try:
        with open(filename, 'r') as file:
            file_contents = file.read()
            for key, value in values_dict.items():
                file_contents = file_contents.replace(f'XXX{key}XXX', str(value))
            file.close()
            return file_contents, {'Content-Type': 'text/html'}
    except OSError as e:
        print("Error:", e)
        

def get_current_time(days_to_add=0):
    from machine import I2C, Pin
    from ds1307 import DS1307
    
    # Get the current time in seconds since the epoch
    I2C_ADDR = 0x68  # DEC 104, HEX 0x68
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
    ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)
    
    # Get the current RTC time as a tuple (year, month, day, hour, minute, second, weekday, yearday)
    current_time = ds1307.datetime
    
    print(current_time)
    # Add delta_days to the current date
    new_time = (
        current_time[0],  # year
        current_time[1],  # month
        current_time[2] ,  # day
        current_time[3],  # hour
        current_time[4],  # minute
        current_time[5],  # second
        current_time[6],  # weekday
        current_time[7]   # yearday
    )
    
    current_timestamp = utime.mktime(current_time)
    
    # Calculate the new timestamp after adding days
    new_timestamp = current_timestamp + (days_to_add * 24 * 60 * 60)
    
    # Convert the new timestamp back to a tuple
    new_time = utime.localtime(new_timestamp)
    
    # Set the new RTC time
    #ds1307.datetime = new_time
    
    # Format the new time as a string
    time_string = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        new_time[0], new_time[1], new_time[2], new_time[3], new_time[4], new_time[5]
    )
    
    return time_string


def get_current_time_old():
    # Get the current time in seconds since the epoch
    I2C_ADDR = 0x68     # DEC 104, HEX 0x68
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
    ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)
    
    # set the RTC time to the current system time
    current_time = ds1307.datetime
    
    # Convert the current time to a tuple (year, month, day, hour, minute, second, weekday, yearday)
    time_tuple = current_time#utime.localtime(current_time)
    
    # Format the time as a string
    time_string = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        time_tuple[0], time_tuple[1], time_tuple[2], time_tuple[3], time_tuple[4], time_tuple[5]
    )
    
    return time_string
   
   
def set_local_time(datetime_str):
    # Split the datetime string into date and time parts
    date, time = datetime_str.split('T')
    year, month, day = map(int, date.split('-'))
    hour, minute = map(int, time.split(':'))
    
    # Convert the datetime components into a UNIX timestamp
    timestamp = (year, month, day, hour, minute, 0, 0, 0)
    print('Setting local time to',(year, month, day, hour, minute, 0, 0, 0))
    # Set the local time
    # DS1307 on 0x68
    I2C_ADDR = 0x68     # DEC 104, HEX 0x68
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
    ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)
    
    # set the RTC time to the current system time
    ds1307.datetime = timestamp
    # get the current RTC time
    print("Current RTC time: {}".format(ds1307.datetime))
    

        
def read_json_config(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = ujson.load(file)
            return json_data
    except OSError:
        return {}  
    file.close()
        
def read_json_config_programas(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = ujson.load(file)
            # Filter out zones that are not 'on' and include minutes for the ones that are on
            # Filter out zones that are not 'on' and include minutes for the ones that are on
            # filtered_data = {}
            # for key, value in json_data.items():
            #     if 'on' in value:
            #         #filtered_data[key] = value
            #         minute_key = f"{key}-minutes"
            #         filtered_data[minute_key] = json_data[minute_key]
            # Order by key
            # ordered_data = dict(sorted(filtered_data.items()))
            ordered_data = dict(sorted(json_data.items()))
            file.close()
            return ordered_data
    except OSError:
        return {}
        

def transform_seteo_programas_json(seteo_programas_json,riego_automatico_json):
    transformed_data = {"p1": {}, "p2": {}, "p3": {}}
    #print('---->',type(input_json),input_json)
    for key, value in seteo_programas_json.items():
        #print('*****',key,value)
        if not 'hora' in key:
            participant, zone = key.split("-")[0], key.split("-")[1]
            print(participant,zone)
            if not value[0] == '00':
                transformed_data[participant][zone] = f'{value[0]} min'

    for num in range(1,4):
        try:
            hora = riego_automatico_json[f'programa_{num}']['hora']
            minuto = riego_automatico_json[f'programa_{num}']['minuto']
            transformed_data['p' + str(num)]['hora_comienzo'] = f"{hora}:{minuto}"
        except:
            transformed_data[f'p{num}']['hora_comienzo'] = f"No configurada"

    return transformed_data

def read_json_config_programa_manual(file_path):
    try:
        with open(file_path, 'r') as file:
            data = ujson.load(file)
            programs = [key for key in data.keys() if key.startswith("programa_") and data[key] == ["on"]]
            filtered_programs = {}
            for program in programs:
                program_number = program.split("_")[1]
                start_hour = data.get(f"programa_{program_number}_start_hour", [""])[0]
                start_minute = data.get(f"programa_{program_number}_start_minute", [""])[0]
                filtered_programs[f"programa_{program_number}"] = {"hora": start_hour, "minuto": start_minute}
            file.close()
            return filtered_programs
    except Exception as e:
        print('Error',e)
        return {}


def read_json_config_programa_automatico(file_path):
    try:
        with open(file_path, 'r') as file:
            data = ujson.load(file)
            riego_automatico = data.get("riego_automatico", [""])[0]
            filtered_programs = {}
            if riego_automatico == "habilitado":
                salida_del_sol = data.get("salida_del_sol", [""])[0]
                puesta_del_sol = data.get("puesta_del_sol", [""])[0]
                filtered_programs["automatico"] = {"salida_del_sol": salida_del_sol}, {"puesta_del_sol": puesta_del_sol}
                file.close()
                return filtered_programs
            else:
                file.close()
                return {}
    except Exception as e:
        return {}


        
def write_json_config(file_path, json_data):
    try:
        with open(file_path, 'w') as file:
            ujson.dump(json_data, file)
            print("JSON data has been written to:", file_path)
    except OSError as e:
        print("Error writing to file:", e)
        return
    file.close()
        

def dict_to_html_table(input_dict):
    html_table = "<table>\n"
    for key, value in input_dict.items():
        if 'hora_comienzo' == key:
            html_table += f"<tr><td><mark>{key}</td><td><mark>{value}</td></tr>\n"
        else:
            html_table += f"<tr><td>{key}</td><td>{value}</td></tr>\n"
    html_table += "</table>"
    return html_table
        
def json_to_html_table(json_data):
    # Check if JSON data is empty or not a list of dictionaries

    if not json_data:
        return '<table><tr><td>Configuracion no encontrada</td></tr></table>'
    
    html_table = "<table border='1'>\n"
    
    # Iterate over the keys of the dictionary
    if json_data:
        #print(json_data,type(json_data))
        for key, value in json_data.items():
            html_table += "<tr>\n"
            
            # Add key as table header
            html_table += f"<th>{key}</th>\n"
            
            # Check if the value is a dictionary
            if isinstance(value, dict):
                # Recursively call the function for nested dictionaries
                html_table += "<td>\n"
                html_table += dict_to_html_table(value)
                html_table += "</td>\n"
            # Check if the value is a list
            elif isinstance(value, list):
                html_table += "<td>\n<ul>\n"
                # Iterate over the list elements
                for item in value:
                    # Check if the list element is a dictionary
                    if isinstance(item, dict):
                        html_table += "<li>\n"
                        html_table += dict_to_html_table(item)
                        html_table += "</li>\n"
                    else:
                        html_table += f"<li>{item}</li>\n"
                html_table += "</ul>\n</td>\n"
            else:
                html_table += f"<td>{value}</td>\n"
            
            html_table += "</tr>\n"
    
    html_table += "</table>"
    
    return html_table
        
