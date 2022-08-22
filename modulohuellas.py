
import time
import board

from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
from rpi_lcd import LCD
from time import sleep

lcd= LCD()

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
#import serial
#uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    lcd.clear()
    lcd.text("Coloque el dedo",2)
    lcd.text(" en el sensor...",3)
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    lcd.clear()
    lcd.text("Modelando...",2)        
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    lcd.clear()
    lcd.text("Buscando...",2)
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="", flush=True)
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="", flush=True)
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="", flush=True)
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="", flush=True)
            lcd.clear()
            lcd.text("Coloque el dedo",2)
            lcd.text(" en el sensor...",3)
        else:
            print("Place same finger again...", end="", flush=True)
            lcd.clear()
            lcd.text("Coloque el mismo",2)
            lcd.text("  dedo de nuevo",3)
        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                lcd.clear()
                lcd.text("Imagen Tomada",2)
                sleep(0.5)
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                lcd.clear()
                lcd.text("ERROR DE IMAGEN",2)
                sleep(2)
                return False
            else:
                print("Other error")
                lcd.clear()
                lcd.text("OTRO ERROR",2)
                sleep(2)
                return False

        print("Templating...", end="", flush=True)
        lcd.clear()
        lcd.text("Modelando Imagen",2)
        i = finger.image_2_tz(fingerimg)
        sleep(0.3)
        if i == adafruit_fingerprint.OK:
            print("Templated")
            lcd.clear()
            lcd.text("Modelada",2)
            sleep(0.5)
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
                lcd.clear()
                lcd.text("Imagen borrosa",2)
                sleep(2)
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
                lcd.clear()
                lcd.text("No se pudo ",2)
                lcd.text("identificar",2)
                sleep(2)
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
                lcd.clear()
                lcd.text("Imagen invalida",2)
                sleep(2)
            else:
                print("Other error")
                lcd.clear()
                lcd.text("OTRO ERROR",2)
                sleep(2)
            return False

        if fingerimg == 1:
            print("Remove finger")
            lcd.clear()
            lcd.text("Quite el dedo",2)  
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    lcd.clear()
    lcd.text("Creando modelo",2)
    i = finger.create_model()
    sleep(0.3)
    if i == adafruit_fingerprint.OK:
        print("Created")
        lcd.clear()
        lcd.text("Creado",2)
        sleep(0.3)
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
            lcd.clear()
            lcd.text("Huellas no ",2)
            lcd.text("coinciden",3)
            sleep(2)
        else:
            print("Other error")
            lcd.clear()
            lcd.text("OTRO ERROR",2)
            sleep(2)
        return False

    print("Storing model #%d..." % location, end="", flush=True)
    lcd.clear()
    lcd.text("Guardando modelo ",2)
    i = finger.store_model(location)
    sleep(0.3)
    if i == adafruit_fingerprint.OK:
        print("Stored")
        lcd.clear()
        lcd.text("GUARDADO ",2)
        sleep(0.5)
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
            lcd.clear()
            lcd.text("ERROR DE",2)
            lcd.text("UBICACION",3)
            sleep(2)
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
            lcd.clear()
            lcd.text("ERROR DE",2)
            lcd.text("ALMACENAMIENTO",3)
            lcd.text("FLASH",4)      
            sleep(2)
        else:
            print("Other error")
            lcd.clear()
            lcd.text("OTRO ERROR",2)
            sleep(2)
        return False

    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i

