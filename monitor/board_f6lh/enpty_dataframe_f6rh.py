import pandas as pd
import datetime

file = '/home/pi/Documents/board/indata_all_f6lh.pkl'
now = datetime.datetime.now()

cols = ["in_time"]
df = pd.DataFrame(columns=cols)
df = df.append({"in_time": now}, ignore_index=True)
print(df)

df.to_pickle(file)
