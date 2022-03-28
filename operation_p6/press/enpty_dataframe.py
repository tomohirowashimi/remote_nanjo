# // 20220212 Ver.hiraoka

import pandas as pd
import datetime
import time

file = '/home/pi/Documents/operation/color_log.pkl'
now = datetime.datetime.now()
time.sleep(1)
now_1 = datetime.datetime.now()
diff_time = now_1 - now

cols = ["time_1", "time_2", "time", "color"]
df = pd.DataFrame(columns=cols)
df = df.append({"time": now, "time": now, "time": diff_time, "color": None}, ignore_index=True)
print(df)

df.to_pickle(file)
