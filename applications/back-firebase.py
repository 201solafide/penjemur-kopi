# Import library yang diperlukan
from serial import Serial
from time import sleep
from os import system
import pyrebase
import json
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from gpiozero import Servo
import RPi.GPIO as GPIO


# Definisi pin GPIO pada Raspberry Pi
PINSERVO = 12
PINZVS = 24


# Konfigurasi Firebase dari file JSON
config = json.load(open("./firebaseConfig.json"))
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("this_is_email@mail.com", "this_is_password")
db = firebase.database()


# Kelas untuk pemrosesan fuzzy logic
class AIProccessing :
    def __init__(self) :
        # Mendefinisikan variabel fuzzy logic
        self.__hum = ctrl.Antecedent(np.arange(20, 91, 1), 'hum')
        self.__tmp = ctrl.Antecedent(np.arange(0, 51, 1), 'tmp')
        self.__pre = ctrl.Antecedent(np.arange(900, 1101, 1), 'pre')
        self.__wet = ctrl.Antecedent(np.arange(0, 101, 1), 'wet')
        self.__out = ctrl.Consequent(np.arange(0, 101, 1), 'out')


        # Menginisialisasi fungsi keanggotaan
        self.__membership()
        # Menetapkan aturan fuzzy
        self.__setRules()


    def __membership(self) :
        # Menentukan fungsi keanggotaan untuk setiap variabel
        self.__hum["low"] = fuzz.trimf(self.__hum.universe, [20, 20, 65])
        self.__hum["medium"] = fuzz.trimf(self.__hum.universe, [20, 60, 80])
        self.__hum["high"] = fuzz.trimf(self.__hum.universe, [75, 90, 90])


        self.__tmp["low"] = fuzz.trimf(self.__tmp.universe, [0, 0, 22])
        self.__tmp["medium"] = fuzz.trimf(self.__tmp.universe, [0, 21, 27])
        self.__tmp["high"] = fuzz.trimf(self.__tmp.universe, [26, 50, 50])


        self.__pre["low"] = fuzz.trimf(self.__pre.universe, [900, 900, 938])
        self.__pre["medium"] = fuzz.trimf(self.__pre.universe, [900, 935, 1011])
        self.__pre["high"] = fuzz.trimf(self.__pre.universe, [1003, 1100, 1100])


        self.__wet["low"] = fuzz.trimf(self.__wet.universe, [0, 0, 50])
        self.__wet["high"] = fuzz.trimf(self.__wet.universe, [45, 100, 100])


        self.__out["low"] = fuzz.trimf(self.__out.universe, [0, 0, 50])
        self.__out["high"] = fuzz.trimf(self.__out.universe, [45, 100, 100])


    def __setRules(self) :
        # Menetapkan aturan fuzzy
        rules = [
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"])
        ]


        boxCtrl = ctrl.ControlSystem(rules)
        self.__boxSim = ctrl.ControlSystemSimulation(boxCtrl)


    def AICompute(self, dataDICT) :
        # Menghitung output fuzzy berdasarkan input
        self.__boxSim.input['hum'] = dataDICT["hum"]
        self.__boxSim.input['tmp'] = dataDICT["tmp"]
        self.__boxSim.input['pre'] = dataDICT["pre"]
        self.__boxSim.input['wet'] = dataDICT["wet"]


        self.__boxSim.compute()


        return round(self.__boxSim.output['out'], 2)


# Program utama
if __name__ == "__main__" :
    # Membuat objek AIProcessing
    callAI = AIProccessing()
    # Menginisialisasi servo dan MiniZVS
    servo = Servo(PINSERVO)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINZVS, GPIO.OUT)


    # Membuka koneksi serial dengan Arduino
    serial = Serial('/dev/ttyACM0', 9600, timeout=1)
    serial.reset_input_buffer()


    try :
        while True :
            # Membersihkan layar terminal
            system("clear")
            # Mengirim perintah "OK" ke Arduino
            serial.write(b"OK\n")


            # Membaca data dari Arduino
            if serial.in_waiting > 0:
                line = serial.readline().decode('utf-8').rstrip()
                dataRAW = line.split(",")
                dataFINAL = {}
                dataFINAL["tmp"] = 0


                # Memproses dan menyimpan data sensor
                for i in range(len(dataRAW)) :
                    temp = dataRAW[i].split(":")
                    if temp[0] == "tmpBMP" or temp[0] == "tmpDHT" :
                        dataFINAL["tmp"] += float(temp[1])
                    elif temp[0] == "pre" :
                        dataFINAL[temp[0]] = round(float(temp[1]) / 100, 2)
                    elif temp[0] == "wet" :
                        dataFINAL[temp[0]] = round((float(temp[1]) / 1023) * 100.00, 2)
                    else :
                        dataFINAL[temp[0]] = round(float(temp[1]), 2)
                dataFINAL["tmp"] = round(float(dataFINAL["tmp"]) / 2, 2)


                # Menghitung output fuzzy menggunakan metode AI
                dataFINAL["fuzz"] = callAI.AICompute(dataFINAL)


                # Kontrol servo dan GPIO berdasarkan output fuzzy
                if dataFINAL["fuzz"] < 50.00 :
                    servo.min()
                    GPIO.output(PINZVS, 1)
                else :
                    servo.max()
                    GPIO.output(PINZVS, 0)


                # Mengirim data ke database Firebase
                db.child(user["localId"]).set(dataFINAL)


                # Menampilkan data di terminal
                print(dataRAW)
                print("")
                print(dataFINAL)


                # Menunggu selama 0.5 detik
                sleep(0.5)
    except Exception as error:
        # Menutup koneksi dan menampilkan pesan kesalahan
        servo.close()
        GPIO.cleanup()
        serial.close()
        print(error)