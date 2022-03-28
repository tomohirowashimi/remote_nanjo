import threading
import picamera
import time
import datetime
import schedule
import traceback
import sys

width = 1024
height = 600

def end_run():
    global state

    state = False

def schedule_run():
    schedule.every().day.at("07:10").do(end_run)
    schedule.every().day.at("19:10").do(end_run)

    while True:
        schedule.run_pending()
        time.sleep(5)

def running():
    global state

    state = True
    while state:    
        try:
            camera = picamera.PiCamera()
            camera.resolution = (width, height)
            
            while True:
                camera.capture('/var/tmp/progress_img.png')
        
                print('--- capture ok ---')
                time.sleep(10)

        except Exception as error:
            print('*** except error ***')
            print(datetime.datetime.now())
            traceback.print_exc()

        finally:
            print('---finally---')
            sys.exit()

if __name__ == '__main__':
    th_schedule = threading.Thread(target=schedule_run, args=())
    th_schedule.start()

    running()
