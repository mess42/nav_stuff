import serial

def raw_angle_to_decimal(raw):
    alpha = float("nan")
    if len(raw) > 0:
        rawfloat = float(raw)
        int_abs = rawfloat // 100
        alpha = int_abs  + (rawfloat - 100 * int_abs) / 60
    return alpha

def raw_to_float(raw):
    flo = float("nan")
    if len(raw) > 0:
        flo = float(raw)
    return flo

def decode_gprmc_sentence(sentence):
    data = sentence[:-3].split(",")[1:]
    
    dec = {"time": data[0],
           "is_active": ( data[1] == "A" ),
           "latitude":  raw_angle_to_decimal( data[2] ) * (1 - 2 * (data[3] == "S") ),
           "longitude": raw_angle_to_decimal( data[4] ) * (1 - 2 * (data[5] == "W") ),
           "speed": raw_to_float(data[6]) * 1.852 / 3.6,
           "azimuth": raw_to_float(data[7]),
           "date": data[8],
           }
    return dec





ser = serial.Serial(
        port="/dev/ttyUSB1", 
        timeout = 0.2
        )
ser.isOpen()


for i in range(20):
    sentence = ser.readline().decode("utf-8")
    print(sentence)
    if sentence.startswith("$GPRMC"):
        print( decode_gprmc_sentence(sentence) )

ser.close()
