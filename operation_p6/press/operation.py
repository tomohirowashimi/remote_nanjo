# // 0302 新規編集

import spidev
import time
import datetime
import pandas as pd
#import schedule
import sys

file = '/home/pi/Documents/operation/color_log.pkl'

timeIn_0 = timeIn_1 = timeIn_3 = datetime.datetime.now()

threshold_0 = 3000
threshold_1 = 3000
threshold_3 = 3000

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

def first_check(data, threshold):
    if data > threshold:
        state = "on"
    else:
        state = "off" 
    return state

def process(data, state, threshold, timeIn, color):
    if state == "off":
        if data > threshold:
            state = "on"
            timeIn = datetime.datetime.now()
        
    elif state == "on":
        if data < threshold:
            state = "off"
            timeOut = datetime.datetime.now()
            timeSpan = (timeOut - timeIn).total_seconds()

            df = pd.read_pickle(file)
            df = df.append({"time_1": timeIn, "time_2": timeOut, "time": timeSpan, "color": color}, ignore_index=True)
            df.to_pickle(file)
            print("write")

            timeIn = timeOut
    
    return state, timeIn

if __name__ == '__main__':   
    ch_0 = spi.xfer2([0x06, 0x00, 0x00])
    data_0 = ((ch_0[1] & 0x0f) << 8) | ch_0[2]
    state_0 = first_check(data_0, threshold_0)

    ch_1 = spi.xfer2([0x06, 0x40, 0x00])
    data_1 = ((ch_1[1] & 0x0f) << 8) | ch_1[2]
    state_1 = first_check(data_1, threshold_1)

    ch_3 = spi.xfer2([0x06, 0xc0, 0x00])
    data_3 = ((ch_3[1] & 0x0f) << 8) | ch_3[2]
    state_3 = first_check(data_3, threshold_3)

    while True:
        try:
            ch_0 = spi.xfer2([0x06, 0x00, 0x00])
            data_0 = ((ch_0[1] & 0x0f) << 8) | ch_0[2]
            color_0 = "green"
            state_0, timeIn_0 = process(data_0, state_0, threshold_0, timeIn_0, color_0)
      
            ch_1 = spi.xfer2([0x06, 0x40, 0x00])
            data_1 = ((ch_1[1] & 0x0f) << 8) | ch_1[2]
            color_1 = "yellow"
            state_1, timeIn_1 = process(data_1, state_1, threshold_1, timeIn_1, color_1)

#            ch_2 = spi.xfer2([0x06, 0x80, 0x00])
#            data_2 = ((ch_2[1] & 0x0f) << 8) | ch_2[2]
#            print("ch_2: ", data_2)

            ch_3 = spi.xfer2([0x06, 0xc0, 0x00])
            data_3 = ((ch_3[1] & 0x0f) << 8) | ch_3[2]
            color_3 = "red"
            state_3, timeIn_3 = process(data_3, state_3, threshold_3, timeIn_3, color_3)

            print(data_0, data_1, data_3)
            time.sleep(10)

        except KeyboardInterrupt:
            spi.close()
            sys.exit()
