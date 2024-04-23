import math

def calculate_julian_day(year, month, day):
    """
    Calculates the Julian day from the given date.
    """
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5

def calculate_sunrise_sunset(latitude, longitude, julian_day, is_sunrise=True):
    """
    Calculates sunrise or sunset time.
    """
    n = julian_day - 2451545.0009 - longitude / 360
    N = 360 / 365.242191 * n
    M = (357.52911 + N) % 360
    C = 1.914602 * math.sin(math.radians(M)) + 0.020421 * math.sin(math.radians(2 * M)) + 0.00052 * math.sin(math.radians(3 * M))
    lambda_sun = (M + C + 180 + 102.9372) % 360
    delta_sun = math.asin(math.sin(math.radians(lambda_sun)) * math.sin(math.radians(23.44)))
    H = math.degrees(math.acos((math.sin(math.radians(-0.83)) - math.sin(math.radians(latitude)) * math.sin(delta_sun)) / (math.cos(math.radians(latitude)) * math.cos(delta_sun))))
    if is_sunrise:
        return 12 - H / 15
    else:
        return 12 + H / 15

def get_sunrise_sunset_times():
    """
    Retrieves sunrise and sunset times for Buenos Aires for the current RTC day
    """
    # Extract date and time components
    from ds1307 import DS1307
    from machine import I2C, Pin
    from time import gmtime, time
    
    # DS1307 on 0x68
    I2C_ADDR = 0x68     # DEC 104, HEX 0x68
    
    # define custom I2C interface, default is 'I2C(0)'
    # check the docs of your device for further details and pin infos
    # this are the pins for the Raspberry Pi Pico adapter board
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
    ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)
    
    # get the current RTC time
    print("Calculating sunrise,sunset times from RTC time: {}".format(ds1307.datetime))
    
    # Calculate Julian day
    julian_day = calculate_julian_day(ds1307.year, ds1307.month, ds1307.day)

    # Buenos Aires coordinates
    latitude = -34.6037
    longitude = -58.3816

    # Calculate sunrise and sunset times
    sunrise_time = calculate_sunrise_sunset(latitude, longitude, julian_day, is_sunrise=True)
    sunset_time = calculate_sunrise_sunset(latitude, longitude, julian_day, is_sunrise=False)

    # Convert decimal time to HH:MM:SS format
    sunrise_hour = int(sunrise_time)
    sunrise_minute = int((sunrise_time - sunrise_hour) * 60)
    sunrise_second = int(((sunrise_time - sunrise_hour) * 60 - sunrise_minute) * 60)

    sunset_hour = int(sunset_time)
    sunset_minute = int((sunset_time - sunset_hour) * 60)
    sunset_second = int(((sunset_time - sunset_hour) * 60 - sunset_minute) * 60)

    return f"{sunrise_hour:02d}:{sunrise_minute:02d}:{sunrise_second:02d}", f"{sunset_hour:02d}:{sunset_minute:02d}:{sunset_second:02d}"

# Example usage
sunrise, sunset = get_sunrise_sunset_times()
print("Sunrise:", sunrise)
print("Sunset:", sunset)
