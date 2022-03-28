# // 20220209 loop 仕様　plan / result
# // 20220223 サフィックス間違い　loop 仕様を最新に修正　→　Wloop仕様に変更
# // 20220224 loop 処理変更 *rh のみ　→　plan 休憩時間処理
# // 20220227 f6用（共通） loop 処理確認

import threading
import tkinter as tk
from tkinter import messagebox
import datetime
import time
import pandas as pd
import csv
import schedule
from dateutil.relativedelta import relativedelta
#from smb.SMBConnection import SMBConnection
import sys
import RPi.GPIO as GPIO

class Board():
    def __init__(self):
        line = "f6lh"     # // *** line uniqe
        if line == "f5":
            self.line_name = "F5"
            product_param = 4
            self.pin = 13
        elif line == "f6lh":
            self.line_name = "F6 LH"
            product_param = 2
            self.pin = 10
        elif line == "f6rh":
            self.line_name = "F6 RH"
            product_param = 2
            self.pin = 10
        else:
            print("*** select error ***")
            time.sleep(5)
            sys.exit()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    

        self.font = 16
        self.font_small = int(self.font * 0.75)
        self.font_large = int(self.font * 1.5)
        self.pad_x = 10
        self.pad_y = 10
        self.fg_label = '#ffffff'
        self.fg_labelDiff = '#ff0000'
        self.bg_label = '#000000'

        file_day = '/home/pi/Documents/board/rest_day.csv'
        file_night = '/home/pi/Documents/board/rest_night.csv'
        file_product_day = '/home/pi/Documents/board/product_' + line[0:2] + '_day.csv'
        file_product_night = '/home/pi/Documents/board/product_' + line[0:2] + '_night.csv'
        self.file_progress = '/var/tmp/progress_' + line + '.pkl'
        self.file_all_indata = '/home/pi/Documents/board/indata_all_' + line + '.pkl'

        self.df_all = pd.read_pickle(self.file_all_indata)
        self.list_intime = []
        self.list_rest = []
        self.list_progress = ["", "", ""]        
        self.state_run = False
        self.state_open = False

        now = datetime.datetime.now()     # // 休憩時間設定
        if datetime.time(7, 30) < now.time() < datetime.time(19, 30):
            with open(file_day, encoding='utf-8', newline='') as f:
                csvreader = csv.reader(f)
                list = [row for row in csvreader]
        else:
            with open(file_night, encoding='utf-8', newline='') as f:
                csvreader = csv.reader(f)
                list = [row for row in csvreader]

        for n in range(1, len(list)):
            for m in range(1, 3):
                if list[n][m] == "":
                    rest = now.replace(year=2099, month=1, day=1, hour=8, minute=0)
                else:
                    rest = datetime.datetime.strptime(list[n][m], '%H:%M')
                rest = self.rest_set(rest, now)
                self.list_rest.append(rest)
        self.list_rest.sort()

        if datetime.time(7, 30) < now.time() < datetime.time(19, 30):     # // 生産条件設定
            with open(file_product_day, encoding='utf-8-sig', newline='') as f:
                csvreader = csv.reader(f)
                list = [row for row in csvreader]
        else:    
            with open(file_product_night, encoding='utf-8-sig', newline='') as f:
                csvreader = csv.reader(f)
                list = [row for row in csvreader]
        self.initial_qua = int(list[0][0]) * product_param
        self.initial_cycle = list[0][1]

        th_schedule = threading.Thread(target=self.schedule, args=())
        th_schedule.start()

    def rest_set(self, rest, now):
        rest_base = now.replace(year=1900, month=1, day=1, hour=8, minute=0)
        if rest.year == 2099:
            rest = rest
        elif rest > rest_base:
            rest = rest.replace(year= now.year, month=now.month, day=now.day)
        else:
            rest = rest.replace(year= now.year, month=now.month, day=now.day)
            rest = rest + relativedelta(days=1)
        return rest

    def gui_set(self):
        self.app = tk.Tk()

        frame_h = tk.Frame(self.app)
        frame_h.pack()
        title = tk.Label(frame_h, text=self.line_name + "　登録画面", font=('', self.font))
        title.pack(padx=self.pad_x, pady=self.pad_y)

        frame_b = tk.Frame(self.app)
        frame_b.pack()
        label_1 = tk.Label(frame_b, text="枚数", font=('', self.font))
        label_4 = tk.Label(frame_b, text="サイクル", font=('', self.font))        
        label_1.grid(column=0, row=0, padx=self.pad_x, pady=self.pad_y)
        label_4.grid(column=1, row=0, padx=self.pad_x, pady=self.pad_y)
        self.entry_1 = tk.Entry(frame_b, font=('', self.font))
        self.entry_4 = tk.Entry(frame_b, font=('', self.font))
        self.entry_1.insert(tk.END, self.initial_qua)
        self.entry_4.insert(tk.END, self.initial_cycle)
        self.entry_1.grid(column=0, row=1, padx=self.pad_x, pady=self.pad_y)
        self.entry_4.grid(column=1, row=1, padx=self.pad_x, pady=self.pad_y)        

        frame_f = tk.Frame(self.app)
        frame_f.pack()
        label_a = tk.Label(frame_f, text="注）登録後は放置！初回入力信号が入ると自動で画面が変わります。", font=('', self.font_small))
        label_b = tk.Label(frame_f, text="注）終了ボタンを押すとアプリケーションが終了します！", font=('', self.font_small), fg=self.fg_labelDiff)
        button_end = tk.Button(frame_f, text="終了", command=self.gui_destroy_app, font=('', self.font_small))
        label_a.pack(padx=self.pad_x, pady=self.pad_y)
        label_b.pack(padx=self.pad_x, pady=self.pad_y)
        button_end.pack(padx=self.pad_x, pady=self.pad_y)

        self.after_id_run = self.app.after(100, self.after_run_check)
        self.after_id_open = self.app.after(100, self.after_open_check)
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing_app)   

        self.app.mainloop()

    def after_run_check(self):
        self.after_id_run = self.app.after(5000, self.after_run_check)
        if self.state_run == False:
            self.state_run = True
            try:
                GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.open_gui_monitor, bouncetime=2000)
            except RuntimeError:
                print("error")
                self.app.after_cancel(self.after_id_run)
                self.state_run = False
                time.sleep(1)
                self.after_run_check()

    def open_gui_monitor(self, pin):
        self.state_open = True

    def after_open_check(self):
        self.after_id_open = self.app.after(5000, self.after_open_check)
        if self.state_open == True:
            self.state_open = False
            self.gui_monitor()
             
    def first_process(self):
        print("first_in")
        GPIO.remove_event_detect(self.pin)
        self.qua = int(self.entry_1.get())
        self.cycle = float(self.entry_4.get()) * 60
        self.startTime = datetime.datetime.now()
        self.countstartTime = datetime.datetime.now()
        self.beforeTime = datetime.datetime.now()
        self.list_intime.append(self.startTime)
        
        self.resultCount = 1
        self.planCount = 1
        self.diffCount = self.resultCount - self.planCount
        self.sv2.set(self.resultCount)
        self.sv3.set(self.diffCount)
        self.sv8.set(self.planCount)

        th_plan = threading.Thread(target=self.thread_planCheck, args=())
        th_plan.start()
        
        time.sleep(1)
        while GPIO.input(self.pin) == GPIO.LOW:
            print("loop", GPIO.input(self.pin))
            time.sleep(0.5)
        print("loop_end")
        
        th_result = threading.Thread(target=self.thread_resultCheck, args=())
        th_result.start()

    def thread_planCheck(self):
        self.state_plan = True
        plan_interval = 5
        while self.state_plan:
            nowTime = datetime.datetime.now()
            
            state_rest = False
            for n in range(1, int(len(self.list_rest)/2)):
                if self.list_rest[2*n-2] < nowTime < self.list_rest[2*n-1]:
                    state_rest = True
                    self.countstartTime = nowTime + datetime.timedelta(seconds=plan_interval)

            if state_rest == False:
                planTime = (nowTime - self.countstartTime).total_seconds()
                if planTime > self.cycle:
                    if self.planCount < self.qua:
                        print("plan_in", self.planCount, self.countstartTime.strftime("%M:%S"))
                        self.planCount += 1     # // plan
                        self.sv8.set(self.planCount)
                    self.calculation(nowTime)
                    self.countstartTime = self.countstartTime + datetime.timedelta(seconds=self.cycle)
            time.sleep(plan_interval)

    def thread_resultCheck(self):
        self.state_result = True
        while self.state_result:
            if GPIO.input(self.pin) == GPIO.LOW:
                nowTime = datetime.datetime.now()        
                newTime = (nowTime - self.beforeTime).total_seconds()     # // new
                self.beforeTime = nowTime
                self.resultCount += 1     # // result
                self.sv2.set(self.resultCount)
                self.sv6.set(int(newTime / 60 * 100))
                self.calculation(nowTime)
                self.list_intime.append(nowTime)
                df_progress = pd.DataFrame(self.list_progress)
                df_progress.to_pickle(self.file_progress)
                print("result_in", self.resultCount)
                
                time.sleep(1)
                while GPIO.input(self.pin) == GPIO.LOW:
                    print("loop", GPIO.input(self.pin))
                    time.sleep(0.5)
                print("loop_end")

            time.sleep(0.5)
    
    def calculation(self, nowTime):
        self.diffCount = self.resultCount - self.planCount     # // diff
        
        adjustTime = 0
        averageSeconds = (nowTime - self.startTime).total_seconds()
        for n in range(1, int(len(self.list_rest)/2+1)):
            if n == 1:
                if self.startTime < self.list_rest[2*n-2]:
                    for m in range(2*n-1, len(self.list_rest), 2):
                        if nowTime > self.list_rest[m]:
                            averageSeconds = averageSeconds - (self.list_rest[m] - self.list_rest[m-1]).total_seconds()
            else:
                if self.list_rest[2*n-4] < self.startTime < self.list_rest[2*n-2]:
                    if self.startTime < self.list_rest[2*n-3]:
                        adjustTime = (self.list_rest[2*n-3] - self.startTime).total_seconds()
                    else:
                        adjustTime = 0
                    for m in range(2*n-1, len(self.list_rest), 2):
                        if nowTime > self.list_rest[m]:
                            averageSeconds = averageSeconds - (self.list_rest[m] - self.list_rest[m-1]).total_seconds()
        averageSeconds = averageSeconds - adjustTime
        if self.resultCount == 1:
            averageCycle = 0
        else:
            averageCycle = averageSeconds / (self.resultCount - 1)     # // average

        finalTime = nowTime + datetime.timedelta(seconds = (self.qua - self.resultCount) * averageCycle)     # // final
        for n in reversed(range(1, int(len(self.list_rest)/2+1))):
            adjustTime = 0
            if n == int(len(self.list_rest)/2):
                if finalTime > self.list_rest[2*n-2]:
                    for m in reversed(range(0, 2*n-1, 2)):
                        if nowTime < self.list_rest[m]:
                            finalTime = finalTime + datetime.timedelta(seconds=(self.list_rest[m+1] - self.list_rest[m]).total_seconds())
                    if finalTime < self.list_rest[2*n-1]:
                        adjustTime = self.list_rest[2*n-1] - finalTime
            else:
                if self.list_rest[2*n] > finalTime > self.list_rest[2*n-2]:
                    for m in reversed(range(0, 2*n-1, 2)):
                        if nowTime < self.list_rest[m]:
                            finalTime = finalTime + datetime.timedelta(seconds=(self.list_rest[m+1] - self.list_rest[m]).total_seconds())
                    for l in reversed(range(n-1, int(len(self.list_rest)/2))):
                        if self.list_rest[2*l] < finalTime < self.list_rest[2*l+1]:
                            adjustTime = self.list_rest[2*l+1] - finalTime
                        else:
                            adjustTime = 0
            if adjustTime != 0:
                finalTime = finalTime + adjustTime

        self.sv3.set(self.diffCount)
        self.sv5.set(int(averageCycle / 60 * 100))
        self.sv7.set(finalTime.strftime("%H時%M分"))
        self.list_progress = [self.diffCount, averageCycle, finalTime]

    def gui_monitor(self):
        self.root = tk.Toplevel()
        self.root.attributes('-zoom', '1')

        self.sv2 = tk.StringVar()
        self.sv3 = tk.StringVar()
        self.sv5 = tk.StringVar()
        self.sv6 = tk.StringVar()
        self.sv7 = tk.StringVar()
        self.sv8 = tk.StringVar()
        
        title = tk.Label(self.root, text=self.line_name + "　進捗モニター", font=('', self.font_large), fg=self.fg_label, bg=self.bg_label)
        label1 = tk.Label(self.root, text="計画", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label2 = tk.Label(self.root, text="実績", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label3 = tk.Label(self.root, text="差異", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label4 = tk.Label(self.root, text="基準", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label5 = tk.Label(self.root, text="平均", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label6 = tk.Label(self.root, text="最新", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label7 = tk.Label(self.root, text="終了", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label8 = tk.Label(self.root, text="予定", font=('', self.font*2), fg=self.fg_label, bg=self.bg_label)
        label_get1 = tk.Label(self.root, text=self.entry_1.get(), font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        label_get4 = tk.Label(self.root, text=int(float(self.entry_4.get())*100), font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        sv_label2 = tk.Label(self.root, textvariable=self.sv2, font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        self.sv_label3 = tk.Label(self.root, textvariable=self.sv3, font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        sv_label5 = tk.Label(self.root, textvariable=self.sv5, font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        sv_label6 = tk.Label(self.root, textvariable=self.sv6, font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        sv_label7 = tk.Label(self.root, textvariable=self.sv7, font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        sv_label8 = tk.Label(self.root, textvariable=self.sv8, font=('', self.font_large*2), fg=self.fg_label, bg=self.bg_label)
        
        title.grid(column=0, row=0, columnspan=3, sticky=(tk.NSEW))
        label1.grid(column=0, row=1)
        label8.grid(column=0, row=2)
        label2.grid(column=0, row=3)
        label3.grid(column=0, row=4)
        label4.grid(column=2, row=1)
        label5.grid(column=2, row=2)
        label6.grid(column=2, row=3)
        label7.grid(column=2, row=4)        
        label_get1.grid(column=1, row=1, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        sv_label8.grid(column=1, row=2, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        sv_label2.grid(column=1, row=3, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        self.sv_label3.grid(column=1, row=4, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        label_get4.grid(column=3, row=1, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        sv_label5.grid(column=3, row=2, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        sv_label6.grid(column=3, row=3, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        sv_label7.grid(column=3, row=4, sticky=(tk.NSEW), padx=self.pad_x, pady=self.pad_y)
        
        button = tk.Button(self.root, text="閉じる", command=self.gui_destroy_root, font=('', self.font_small))
        button.grid(column=3, row=0, padx=self.pad_x, pady=self.pad_y)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.configure(bg=self.bg_label)
        
        self.first_process()
        self.after_id_config = self.root.after(100, self.after_config)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_root)
        self.root.mainloop()

    def after_config(self):
        self.after_id_config = self.root.after(10000, self.after_config)
        if self.diffCount < 0:
            self.sv_label3.config(foreground=self.fg_labelDiff)
        else:
            self.sv_label3.config(foreground=self.fg_label)

    def on_closing_root(self):
        if messagebox.askokcancel("閉じる", "モニター画面を閉じますか？", parent=self.root):
            self.gui_destroy_root()
    
    def on_closing_app(self):
        if messagebox.askokcancel("閉じる", "アプリケーションを終了しますか？"):
            self.gui_destroy_app()

    def gui_destroy_root(self):
        cols = ["in_time"]
        df_today = pd.DataFrame(self.list_intime, columns=cols)
        df = self.df_all.append(df_today)
        df.to_pickle(self.file_all_indata)

        self.entry_1.delete(0, tk.END)
        self.entry_1.insert(tk.END, self.qua - self.resultCount)
        self.root.after_cancel(self.after_id_config)
        self.state_plan = False
        self.state_result = False
        self.state_run = False
        self.root.destroy()
        print("--- close ---")

    def gui_destroy_app(self):
#        self.smbc_send()
        self.app.after_cancel(self.after_id_run)
        self.app.after_cancel(self.after_id_open)
        self.state_schedule = False
        GPIO.cleanup()
        self.app.destroy()
        print("--- end ---")
        sys.exit()
       
    def smbc_send(self):
        conn = SMBConnection(
            'robot',
            'vehicle',
            platform.uname().node,
            'PC19022',
            domain='',
            use_ntlm_v2=True)
        conn.connect('192.168.107.181', 139)
        print(conn.echo('echo success'))

        with open(self.file_all_indata, 'rb') as f:
            conn.storeFile('robot', '/monitor_data/' + self.file_all_indata, f)

    def schedule(self):
        schedule.every().day.at("07:40").do(self.gui_destroy_root)
        schedule.every().day.at("07:41").do(self.gui_destroy_app)
        schedule.every().day.at("19:40").do(self.gui_destroy_root)
        schedule.every().day.at("19:41").do(self.gui_destroy_app)
        
        self.state_schedule = True
        while self.state_schedule:
            schedule.run_pending()
            time.sleep(120)

if __name__ == '__main__':
    board = Board()
    board.gui_set()
