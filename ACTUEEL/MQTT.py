import time
import utime
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
import json
gc.collect()
import _thread
import stock_management

#msg = 0
#print(stock_management.artikel_send)
#merker_led = False

#EXAMPLE IP ADDRESS
mqtt_server = '159.223.224.138'

client_id = ubinascii.hexlify(machine.unique_id())

nr_automaat = 3   #vul nummer automaat in
naam_automaat = "hal5_korteketen"
aantal_plateaus = 4
topic_adjust = "automaat_" + str(nr_automaat) + "/telemetrie/send"
topic_receive = "automaat_" + str(nr_automaat) + "/telemetrie/receive"
topic_send ="automaat_" + str(nr_automaat) + "/settings_telemetrie/send"
topic_temp = "automaat_" + str(nr_automaat) + "/temperatuur"
topic_verkocht = "automaat_" + str(nr_automaat) + "/verkocht"
topic_watchdog = "automaat_" + str(nr_automaat) + "/watchdog"


ssid = "BOERENSCHUUR";
password = "Helholtp1!";

#ssid = "TP-Link_AD1C";
#password = "Helholink1!";

sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
  print('connecting to network...')
  sta.active(True)
  #sta.connect('your wifi ssid', 'your wifi password')
  sta.connect(ssid, password)
  while not sta.isconnected():
    pass
    
print('Connection WiFi successful')    
print('network config:', sta.ifconfig())

def sub_cb(topic, msg):
    global topic_adjust
    if topic.decode() == topic_receive and msg.decode() == 'get_settings':
        f = open("VMC_parameters.json","rt")
        current_settings = f.read()
        print("Settings are",current_settings)
        f.close()
        time.sleep(0.1)
        client.publish(topic_adjust, current_settings)
    if topic.decode() == topic_send:
        #print(msg.decode())
        f = open("VMC_parameters.json","wt")
        f.write(msg.decode())
        #print(msg.decode())
        #print("stock aangepast door node-red")
        f.close()

def connect_and_subscribe():
    global client_id, mqtt_server, topic_adjust,topic_receive, topic_send,topic_temp,topic_verkocht
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_adjust)
    client.subscribe(topic_receive)
    client.subscribe(topic_send)
    client.subscribe(topic_temp)
    client.subscribe(topic_verkocht)
    client.subscribe(topic_watchdog)
    print('Connected to %s MQTT broker, subscribed to topic >> %s ' % (mqtt_server, topic_adjust))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

def send_VMC_parameters():
    global topic_adjust
    f = open("VMC_parameters.json","rt")
    current_settings = f.read()
    #print("Settings are",current_settings)
    f.close()
    print("stock wordt aangepast")
    client.publish(topic_adjust, current_settings)

def send_sold(msg):
    global topic_verkocht
    client.publish(topic_verkocht, msg)
    
def watchdog(msg):
    global topic_watchdog
    client.publish(topic_watchdog, msg)

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

def check_msg():
    global client
    while True:
        
        try:
            client.check_msg()
        except OSError as e:
            restart_and_reconnect()
        
        #time.sleep(0.1)
        #print("loop mqtt")
_thread.start_new_thread(check_msg,())
