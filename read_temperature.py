import os
import random

# we checking for a real Pi - this code will also work on your computer
real_pi = True
try:
    import RPi.GPIO as GPIO
    real_pi = True
except:
    real_pi = False

def current_cpu_temperature():
    # gets the current CPU temperature of the Pi
    if real_pi:
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").readline()
        temp = temp.replace("temp=","")
        temp = temp.replace("'C","")
        return float(temp)
    else:
        return 50 + int(random.random()*100)/100