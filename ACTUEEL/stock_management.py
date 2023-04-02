#221207: MIT ap stuurt string door op settings_obj["artikelen"][p]["aantal"].  Aanpassen naar integer
import json
import time
import MQTT
from machine import Pin
import _thread

#knop_verkoop = DebouncedSwitch(Pin(6, Pin.IN))
knop_verkoop = Pin(13, Pin.IN, Pin.PULL_UP)


#artikel_send = ""
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
print("stock management started")
print("knop_verkoop status =",knop_verkoop.value())


def stock_decrement(plateau):
    if knop_verkoop.value() == 1:#checkt of automaat in stand verkoop staat"
        #print(knop_verkoop)
        #print("plateau",plateau)
        p= int(plateau)-1
        try:
            global artikel_send
            f = open("VMC_parameters.json","rt")
            current_settings = f.read()
            #print("Settings are",current_settings)
            f.close()
            settings_obj = json.loads(current_settings)
            #print(settings_obj)
            
            ### MIT AP stuurt aantal door als string --> aanpassen naar integer
            #print(type(settings_obj["artikelen"][p]["aantal"]))
            settings_obj["artikelen"][p]["aantal"] = int(settings_obj["artikelen"][p]["aantal"])
            #print(type(settings_obj["artikelen"][p]["aantal"]))
            
            if settings_obj["artikelen"][p]["aantal"] >= 0:
                settings_obj["artikelen"][p]["aantal"] -=1
            print("stock is :",settings_obj["artikelen"][p]["aantal"])
            current_settings = json.dumps(settings_obj)
            f = open("VMC_parameters.json","wt")
            f.write(current_settings)
            f.close()
            MQTT.send_VMC_parameters()
            #print(settings_obj["artikelen"][p]["artikel"])
            artikel_send = str(settings_obj["artikelen"][p]["artikel"])
            print("er is een",artikel_send, "verkocht")
            MQTT.send_sold(artikel_send)
              

        except:
            print("Error during saving") 
            time.sleep(1)
        #MQTT.send_sold(artikel)      
        MQTT.send_sold(artikel_send)
    else:
        print("automaat niet in stand verkoop")

def watchdog():
    last_message = 0
    message_interval = 10
    while True:
        print("watchdog activated")
        time.sleep(5)
        try:
            if (time.time() - last_message) > message_interval:
                MQTT.watchdog(str(knop_verkoop.value()))
                last_message = time.time()
        except OSError as e:
            pass
            #restart_and_reconnect()
        
_thread.start_new_thread(watchdog,())
