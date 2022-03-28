# // 20220204 資材庫用新規作成

import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFile
import csv
import datetime
import time
import platform
from smb.SMBConnection import SMBConnection
import traceback
import sys
from io import BytesIO
import pathlib
import pandas as pd

class Progress():
    def __init__(self):
        self.ip_lh = '192.168.107.20'
        self.ip_rh = '192.168.107.21'
        self.ip_f5 = '192.168.107.242'
        self.ip_img = '192.168.107.22'
        self.file_lh = 'progress_f6lh.pkl'
        self.file_rh = 'progress_f6rh.pkl'
        self.file_f5 = 'progress_f5.pkl'
        self.file_img = 'progress_img.png'

        self.change_time = 10
    
    def smbc_connect(self, ip, file):
        conn = SMBConnection(
            'pi',
            'silvia',
            platform.uname().node,
            'raspberry pi',
            domain='',
            use_ntlm_v2=True)
        
        conn.connect(ip, 139)
        print(conn.echo('echo success'))

        with open(file, 'wb') as f:
            conn.retrieveFile('pi', file, f)

        conn.close()

    def set(self, file):
        df = pd.read_pickle(file)
        average = df.iat[1, 0]
        diff = df.iat[0, 0]
        final = df.iat[2, 0]

        return (average, diff, final)

    def change_data(self):
        while self.state:
            try:
                print('-----span---')
                print('-- change_lh')
                self.smbc_connect(self.ip_lh, self.file_lh)
                outcome = self.set(self.file_lh)
                self.sv_average_lh.set(int(outcome[0] / 60 * 100))
                self.sv_diff_lh.set(outcome[1])
                self.sv_final_lh.set(outcome[2].strftime("%H:%M"))

                print('-- change_rh')
                self.smbc_connect(self.ip_rh, self.file_rh)
                outcome = self.set(self.file_rh)
                self.sv_average_rh.set(int(outcome[0] / 60 * 100))
                self.sv_diff_rh.set(int(outcome[1]))
                self.sv_final_rh.set(outcome[2].strftime("%H:%M"))

                print('-- change_f5')
                self.smbc_connect(self.ip_f5, self.file_f5)
                outcome = self.set(self.file_f5)
                self.sv_average_f5.set(int(outcome[0] / 60 * 100))
                self.sv_diff_f5.set(int(outcome[1]))
                self.sv_final_f5.set(outcome[2].strftime("%H:%M"))

                print('-- change_img')
                self.smbc_connect(self.ip_img, self.file_img)
                
                time.sleep(self.change_time)
                
            except Exception as error:
                print('*** except _error (data)')
                print(datetime.datetime.now())
                traceback.print_exc()
                time.sleep(self.change_time)
                
            finally:
                pass

    def change_img(self):
        try:
            Image.LOAD_TRUNCATED_IMAGES = True
            img = Image.open(self.file_img)
            self.canvas.photo = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self.on_canvas, image=self.canvas.photo)
            self.sv_judgementImg.set('')
            self.after_id = self.root.after(self.change_time * 1000, self.change_img)
            
        except Exception as error:
            print('*** except_error (img)')
            self.state = False
            self.th.join()
            self.root.after_cancel(self.after_id)
            self.sv_judgementImg.set('error')
            time.sleep(self.change_time)
            self.thread()
            self.after_id = self.root.after(self.change_time * 1000, self.change_img)
            
        finally:
            pass

    def thread(self):
        self.state = True
        self.th = threading.Thread(target=self.change_data, args=())
        self.th.start()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.after_cancel(self.after_id)
            self.state = False
            
            self.root.destroy()
        sys.exit()

    def gui(self):
        font = 20
        font_large = int(font * 2)
        font_large_label = int(font * 1.25)
        pad_y = 10
        pad_x = 50
        fg_blu = '#0000ff'
        fg_red = '#ff0000'

        self.root = tk.Tk()
        self.root.title(u'資材庫用モニター')
#        self.root.state('zoomed')

        img = Image.new('RGB', (1024, 600))
        img.save(self.file_img, 'png')

        frame_data_lh = tk.Frame(self.root)
        frame_data_rh = tk.Frame(self.root)
        frame_data_f5 = tk.Frame(self.root)
        frame_image = tk.Frame(self.root)
        frame_data_f5.pack(side=tk.LEFT)
        frame_data_lh.pack(side=tk.LEFT)
        frame_data_rh.pack(side=tk.RIGHT)
        frame_image.pack(expand=True)

        Image.LOAD_TRUNCATED_IMAGES = True
        img = Image.open(self.file_img)
        img = ImageTk.PhotoImage(img)
        self.canvas = tk.Canvas(frame_image, width=1024, height=600, bg='#ffffff')
        self.on_canvas = self.canvas.create_image(412, 300, image=img)
        self.sv_judgementImg = tk.StringVar()
        label_sv_judgementImg = tk.Label(frame_image, textvariable=self.sv_judgementImg, font=('', int(font_large*1.5)), fg=fg_red)

        label_lh =tk.Label(frame_data_lh, text="[F6LH]", font=('', font_large_label), fg=fg_red)
        label_average_lh = tk.Label(frame_data_lh, text="(平均)", font=('', font))
        label_diff_lh = tk.Label(frame_data_lh, text="(差異)", font=('', font))
        label_final_lh = tk.Label(frame_data_lh, text="(終了)", font=('', font))
        self.sv_average_lh = tk.StringVar()
        self.sv_diff_lh = tk.StringVar()
        self.sv_final_lh = tk.StringVar()
        label_sv_average_lh = tk.Label(frame_data_lh, textvariable=self.sv_average_lh, font=('', font_large), fg=fg_blu)
        label_sv_diff_lh = tk.Label(frame_data_lh, textvariable=self.sv_diff_lh, font=('', font_large), fg=fg_blu)
        label_sv_final_lh = tk.Label(frame_data_lh, textvariable=self.sv_final_lh, font=('', font_large), fg=fg_blu)

        label_rh =tk.Label(frame_data_rh, text="[F6RH]", font=('', font_large_label), fg=fg_red)
        label_average_rh = tk.Label(frame_data_rh, text="(平均)", font=('', font))
        label_diff_rh = tk.Label(frame_data_rh, text="(差異)", font=('', font))
        label_final_rh = tk.Label(frame_data_rh, text="(終了)", font=('', font))
        self.sv_average_rh = tk.StringVar()
        self.sv_diff_rh = tk.StringVar()
        self.sv_final_rh = tk.StringVar()
        label_sv_average_rh = tk.Label(frame_data_rh, textvariable=self.sv_average_rh, font=('', font_large), fg=fg_blu)
        label_sv_diff_rh = tk.Label(frame_data_rh, textvariable=self.sv_diff_rh, font=('', font_large), fg=fg_blu)
        label_sv_final_rh = tk.Label(frame_data_rh, textvariable=self.sv_final_rh, font=('', font_large), fg=fg_blu)

        label_f5 =tk.Label(frame_data_f5, text="[F5]", font=('', font_large_label), fg=fg_red)
        label_average_f5 = tk.Label(frame_data_f5, text="(平均)", font=('', font))
        label_diff_f5 = tk.Label(frame_data_f5, text="(差異)", font=('', font))
        label_final_f5 = tk.Label(frame_data_f5, text="(終了)", font=('', font))
        self.sv_average_f5 = tk.StringVar()
        self.sv_diff_f5 = tk.StringVar()
        self.sv_final_f5 = tk.StringVar()
        label_sv_average_f5 = tk.Label(frame_data_f5, textvariable=self.sv_average_f5, font=('', font_large), fg=fg_blu)
        label_sv_diff_f5 = tk.Label(frame_data_f5, textvariable=self.sv_diff_f5, font=('', font_large), fg=fg_blu)
        label_sv_final_f5 = tk.Label(frame_data_f5, textvariable=self.sv_final_f5, font=('', font_large), fg=fg_blu)

        label_f5.pack(padx=pad_x, pady=int(pad_y*1.5))
        label_average_f5.pack(padx=pad_x, pady=pad_y)
        label_sv_average_f5.pack(padx=pad_x, pady=pad_y)
        label_diff_f5.pack(padx=pad_x, pady=pad_y)
        label_sv_diff_f5.pack(padx=pad_x, pady=pad_y)
        label_final_f5.pack(padx=pad_x, pady=pad_y)
        label_sv_final_f5.pack(padx=pad_x, pady=pad_y)
        label_lh.pack(padx=pad_x, pady=int(pad_y*1.5))
        label_average_lh.pack(padx=pad_x, pady=pad_y)
        label_sv_average_lh.pack(padx=pad_x, pady=pad_y)
        label_diff_lh.pack(padx=pad_x, pady=pad_y)
        label_sv_diff_lh.pack(padx=pad_x, pady=pad_y)
        label_final_lh.pack(padx=pad_x, pady=pad_y)
        label_sv_final_lh.pack(padx=pad_x, pady=pad_y)
        label_sv_judgementImg.pack()
        self.canvas.pack()
        label_rh.pack(padx=pad_x, pady=int(pad_y*1.5))
        label_average_rh.pack(padx=pad_x, pady=pad_y)
        label_sv_average_rh.pack(padx=pad_x, pady=pad_y)
        label_diff_rh.pack(padx=pad_x, pady=pad_y)
        label_sv_diff_rh.pack(padx=pad_x, pady=pad_y)
        label_final_rh.pack(padx=pad_x, pady=pad_y)
        label_sv_final_rh.pack(padx=pad_x, pady=pad_y)

        self.thread()
        self.after_id = self.root.after(self.change_time * 1000, self.change_img)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()

if __name__ == "__main__":
    progress = Progress()
    progress.gui()
