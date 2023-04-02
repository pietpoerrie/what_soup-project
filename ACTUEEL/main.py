from machine import Pin
import time
import stock_management

#pinnr = [23,22,21,19,18,17,16,0,15,34]
pinnr = [23,22,21,19,18,17]

def irqHandler(pin):

    #check to see if the level is still low after 100ms
    time.sleep(0.1)
    if pin.value() == 1:
        return
    #wait untill the pin goes high again before action
    while pin.value() == 0:
        time.sleep(0.1)
    #get pinnr from the pin string
    nr = int(str(pin)[4:].rstrip(')'))
    #find the pinnr index
    index = pinnr.index(nr) + 1
    stock_management.stock_decrement(index)
    #print(pin)

for x in pinnr:
    p = Pin(x,Pin.IN)
    p.irq(irqHandler,Pin.IRQ_FALLING)

while 1:
    time.sleep(1)
    print("waiting for button push...")
