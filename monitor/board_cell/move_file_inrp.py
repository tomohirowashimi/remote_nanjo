# // 20220217 新規作成

import shutil

line_name = "12"

oldPath_day = "/var/tmp/product_" + line_name + "_day.csv"
oldPath_night = "/var/tmp/product_" + line_name + "_night.csv"
newPath_day = "/home/pi/Documents/board/product_" + line_name + "_day.csv"
newPath_night = "/home/pi/Documents/board/product_" + line_name + "_night.csv"

shutil.copy(oldPath_day, newPath_day)
shutil.copy(oldPath_night, newPath_night)
