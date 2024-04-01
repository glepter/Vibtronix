from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.font import Font
from datetime import date
from datetime import datetime as dtime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from openpyxl.workbook.workbook import Workbook
import time
from threading import *
import numpy as np
import serial.tools.list_ports
import serial
import socket
import csv




ser = serial.Serial(baudrate=115200, timeout=2)

#Creamos clase para Objeto que genera y maneja la UI (Interfaz de Usuario) y su funcionalidad.
class UI:

    #Inicializa el objeto, requiere una hoja de excel como argumento.
    def __init__(self, master, ser):
        #Crea variable interna para controlar el libro y la hoja de excel.
        #Crea variable interna para Objeto Serial. Crea variable para el root de TKInter y asigna titulo.
        self.ser = ser
        self.sampleCount = 1500
        self.classID = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
        self.header = ['Instance', 'Class', 'Timestamp', 'Acc X', 'Acc Y', 'Acc Z', 'Gyro X', 'Gyro Y', 'Gyro Z']
        self.sensorDat = [[],[],[],[],[],[]]
        self.serverAddr = '10.0.0.21'
        self.serverPort = 12345
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.serverAddr, self.serverPort))



        self.master = master
        self.master.title("Interfaz")
        self.master.geometry('1152x550')
        #Crea un contenedor para la pagina principal (Frame).
        self.First = Frame(self.master)
        


        Accel = LabelFrame(self.First, text="Acelerometro", bd=2)
        Accel.grid(row=0, column=0, columnspan=5, padx=10, pady=(5,25), ipadx=2, ipady=2)
        #Crea figura para contener las graficas.
        self.fig1 = Figure(dpi= 50, facecolor='Black', constrained_layout=True)
        #Crea y configura un area de dibujo de TKinter para contener la figura.       
        self.cs1 = FigureCanvasTkAgg(self.fig1, master=Accel)
        self.cs1.draw()
        self.cs1.get_tk_widget().grid(row=0, column=1, rowspan=4, sticky=E)
        #Crea y configura Labels para contener el valor actual.
        self.Accelx = Label(Accel, text="x", font=("Verdana",14))
        self.Accelx.grid(row=0, column=3, sticky=E, pady=4, padx=5)
        self.Accely = Label(Accel, text="y", font=("Verdana",14))
        self.Accely.grid(row=1, column=3, sticky=E, pady=4, padx=5)
        self.Accelz = Label(Accel, text="z", font=("Verdana",14))
        self.Accelz.grid(row=2, column=3, sticky=E, pady=4, padx=5)
        #Crea Etiquetas para identificar las graficas.
        Ax = Label(Accel, text="Accel x", font=("Verdana",16))
        Ax.grid(row=0, column=0, sticky=E, pady=4, padx=5)
        #Crea y define Boton para el Sensor 2.
        Ay = Label(Accel, text="Accel y", font=("Verdana",16))
        Ay.grid(row=1, column=0, sticky=E, pady=4, padx=5)
        #Crea y define Boton para el Sensor 3.
        Az = Label(Accel, text="Accel z", font=("Verdana",16))
        Az.grid(row=2, column=0, sticky=E, pady=4, padx=5)


        Gyro = LabelFrame(self.First, text="Giroscopio", bd=2)
        Gyro.grid(row=0, column=6, columnspan=5, padx=10, pady=(5,25), ipadx=2, ipady=2)
        #Crea figura para contener las graficas.
        self.fig2 = Figure(dpi= 50, facecolor='Black', constrained_layout=True)
        #Crea y configura un area de dibujo de TKinter para contener la figura.       
        self.cs2 = FigureCanvasTkAgg(self.fig2, master=Gyro)
        self.cs2.draw()
        self.cs2.get_tk_widget().grid(row=0, column=1, rowspan=4, sticky=E)
        #Crea y configura Labels para contener el valor actual.
        self.Gyrox = Label(Gyro, text="x", font=("Verdana",14))
        self.Gyrox.grid(row=0, column=3, sticky=E, pady=4, padx=5)
        self.Gyroy = Label(Gyro, text="y", font=("Verdana",14))
        self.Gyroy.grid(row=1, column=3, sticky=E, pady=4, padx=5)
        self.Gyroz = Label(Gyro, text="z", font=("Verdana",14))
        self.Gyroz.grid(row=2, column=3, sticky=E, pady=4, padx=5)
        #Crea Etiquetas para identificar las graficas.
        Gx = Label(Gyro, text="Pitch", font=("Verdana",16))
        Gx.grid(row=0, column=0, sticky=E, pady=4, padx=(25,15))
        #Crea y define Boton para el Sensor 2.
        Gy = Label(Gyro, text="Roll", font=("Verdana",16))
        Gy.grid(row=1, column=0, sticky=E, pady=4, padx=(25,15))
        #Crea y define Boton para el Sensor 3.
        Gz = Label(Gyro, text="Yaw", font=("Verdana",16))
        Gz.grid(row=2, column=0, sticky=E, pady=4, padx=(25,15))





        #Crea y define texto y dropdown menu del contador de minutos.
        lsample = Label(self.First, text="Numero de Muestras",font=Font(family='Helvetica', size=13, weight='normal'), highlightthickness=0)
        lsample.grid(row=2, column=0)
        self.spin = Spinbox(self.First,  from_= 1000, to = 10000, increment = 10, wrap = True, width=5, highlightthickness=0, border=0, font=Font(family='Helvetica', size=13, weight='normal'))   
        self.spin.delete(0,"end")
        self.spin.insert(0,1500)
        self.spin.grid(row=2,column=1, sticky=W)

        lclassid = Label(self.First, text="Clase: ",font=Font(family='Helvetica', size=13, weight='normal'), highlightthickness=0)
        lclassid.grid(row=3, column=0)
        self.spin2 = Spinbox(self.First, values=self.classID, wrap = True, width=5, highlightthickness=0, border=0, font=Font(family='Helvetica', size=13, weight='normal'))   
        self.spin2.grid(row=3,column=1, sticky=W)

        #Crea y define Botones de funciones y manda llamar sus respectivas subrutinas.
        self.breport = Button(self.First, text="Reporte", width=10, height=2, command=self.report)
        self.breport.grid(row=2, column=9, padx=35, pady=10)
        self.bstop = Button(self.First, text="Desconectar", width=10, height=2, command=self.master.destroy)
        self.bstop.grid(row=3, column=9, padx=55, pady=5)
        self.bresume = Button(self.First, text="Continuar", width=10, height=2, command= self.threading)
        self.bresume.grid(row=4, column=9, padx=35, pady=5)
        #Asigna contenedor a la pantalla principal (default).
        self.First.grid()


    #Funcion para generar reporte, crea un TopLevel (segunda pantalla que toma el frente cuando aparece)
    #con las opciones para generar el reporte.
    def report(self):
        #Crea y define TopLevel y asigna a Root (Objeto), define en una estructura de grid.
        self.Second = Toplevel(self.master)
        #Crea Label Frame para contener parte de las opciones.
        frame = LabelFrame(self.Second, text="Reporte")
        frame.grid(row=0, column=0, columnspan=3, padx=15, pady=10)
        #Crea y define el texto de las opciones.
        flab = Label(frame, text="Desde: ")
        flab.grid(row=1 , column=0, pady=0, padx=20)
        tlab = Label(frame, text="hasta: ")
        tlab.grid(row=2 , column=0, pady=10, padx=20)
        #Crea Objeto datetime (declarado en el header).
        d = date.today()
        #Asigna valores obtenidos del Objeto a las varibles internas declaradas en el main.
        dia.set(d.day)
        mes.set(d.month)
        #La funcion ofrece 5 dias de reporte en modo por defecto, en caso de que la diferencia de los
        #dias incluya dos meses distintos esta condicion lo controla restando los dias predeterminados o 
        #agregandoselos a 25 (considerando un mes de 30 dias, 30-5+los dias del mes, ie: request en
        #Febrero 3, 5 dias antes es 29 de Enero :. 30-5=25+3=28, el dia faltante se da porque por
        #simplicidad se considera un mes de 30 dias).
        if d.day > 5:
            ddia.set(d.day-5)
            mmes.set(d.month)
        else:
            ddia.set(25+d.day)
            mmes.set(d.month-1)
        anio.set(d.year)
        #Crea y define Labels para texto de las opciones.
        dlab = Label(frame, text="Dia")
        dlab.grid(row=0, column=1, pady=2, padx=10)
        mlab = Label(frame, text="Mes")
        mlab.grid(row=0, column=2, pady=2, padx=10)
        alab = Label(frame, text="Año")
        alab.grid(row=0, column=3, pady=2, padx=10)
        #Crea y define menus tipo Dropdown de la primera seccion con los valores predeterminados calculados arriba.
        self.fdia = Spinbox(frame, from_= 0, to = 31, wrap = True, width=4, textvariable=ddia, font=Font(family='Helvetica', size=9, weight='normal'))
        self.fdia.delete(0,"end")
        self.fdia.insert(0,d.day-7)
        self.fdia.grid(row=1, column=1, pady=5, padx=10)
        self.fmes = Spinbox(frame, from_= 0, to = 12, wrap = True, width=4, textvariable=mmes, font=Font(family='Helvetica', size=9, weight='normal'))
        self.fmes.delete(0,"end")
        self.fmes.insert(0,d.month)
        self.fmes.grid(row=1, column=2, pady=5)
        self.fanio = Spinbox(frame, from_= d.year, to = d.year+4, wrap = True, width=4, textvariable=anio, font=Font(family='Helvetica', size=9, weight='normal'))
        self.fanio.grid(row=1, column=3, pady=5, padx=10)    
        #Crea y define los menus de la segunda seccion.
        self.sdia = Spinbox(frame, from_= 0, to = 31, wrap = True, width=4, textvariable=dia, font=Font(family='Helvetica', size=9, weight='normal'))
        self.sdia.delete(0,"end")
        self.sdia.insert(0,d.day)
        self.sdia.grid(row=2 , column=1, pady=5, padx=10)
        self.smes = Spinbox(frame, from_= 0, to = 12, wrap = True, width=4, textvariable=mes, font=Font(family='Helvetica', size=9, weight='normal'))
        self.smes.delete(0,"end")
        self.smes.insert(0,d.month)
        self.smes.grid(row=2 , column=2, pady=5)
        self.sanio = Spinbox(frame, from_= d.year, to = d.year+4, wrap = True, width=4, textvariable=anio, font=Font(family='Helvetica', size=9, weight='normal'))
        self.sanio.grid(row=2 , column=3, pady=5, padx=10)
        #Crea y define Botones para cancelar o exportar reporte.
        gen = Button(self.Second, text="Generar", width=10, height=2, command= lambda : self.generate() & self.Second.destroy())
        gen.grid(row=2, column=0, padx=10, pady=10)
        cancel = Button(self.Second, text="Cancelar", width=10, height=2, command= lambda : self.activate() & self.Second.destroy())
        cancel.grid(row=2, column=2, padx=20, pady=5)
        self.Second.grid()


    #F
    def generate(self):
        self.activate()
        pass


    def readFile(self):
        try:
            self.server_socket.close()
        except:
            print("Inicializando")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.serverAddr, self.serverPort))
        list=[]
        x=0
        while True:
            # Receive data from the client
            data, client_address = self.server_socket.recvfrom(1024)            
            d = dtime.now()
            print(f"Received from {client_address}: {data.decode('utf-8')}")
            info=str(data.decode('utf-8')).replace(')','')
            info=info.replace('(','')
            #print(info)
            info=info.split(',')
            aux=[x,self.spin2.get(), d.strftime("%H:%M:%S")]
            print(aux+info)            
            list.append(aux+info)

            for i in range(len(self.sensorDat)):
                self.sensorDat[i].append(info[i])
            
            #print(info[1],info[4])
            self.Accelx['text'] = str(info[0])+"*"
            self.Accely['text'] = str(info[1])+"*"
            self.Accelz['text'] = str(info[2])+"*"
            self.Gyrox['text'] = str(info[3])+"*"
            self.Gyroy['text'] = str(info[4])+"*"
            self.Gyroz['text'] = str(info[5])+"*"




            x=x+1
            if x>int(self.spin.get()):
                self.updateGraph()
                break
        self.server_socket.close()
        self.file_name = "output"+self.spin2.get()+".csv"
        with open(self.file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.header) 
            writer.writerows(list) 
        print(f"CSV file '{self.file_name}' has been created.")
        
            


    #Funcion para establecer comunicacion con Arduino usando el Objeto de serial creado al inicio.
    def connectSerial(self):
        
        #Crea Toplevel y Label Frame para contener parte de las opciones.
        self.ConnectWindow = Toplevel(self.master, height=500, width= 500)
        frame = LabelFrame(self.ConnectWindow, text="Puertos disponibles")
        frame.grid(row=0, column=0, columnspan=3, sticky=N+S+E+W, padx=15, pady=10)
        #Cierra cualquier coneccion abierta para evitar problemas.
        self.ser.close()
        #Crea una lista de Python con el retorno de la funcion llamada, obtiene y almacena datos obtenidos.
        ports = list(serial.tools.list_ports.comports())
        self.items = StringVar()
        self.portsDict = {x.description:x.name for x in ports}
        self.items.set([x.description for x in ports])
        #Crea Listbox para los puertos disponibles.
        self.list = Listbox(frame, listvariable=self.items, width=35)
        self.list.select_set(0)
        self.list.grid(row=0, column=0, sticky=N+S+E+W, padx=15, pady=10)
        #Crea Botones para controlar las funciones.
        cncel = Button(self.ConnectWindow, text="Cancelar", width=10, height=2, command= lambda : self.activate() & self.ConnectWindow.destroy())
        cncel.grid(row=1, column=0, padx=30, pady=10)
        connect = Button(self.ConnectWindow, text="Connectar", width=10, height=2, command= lambda : self.activate() & self.Connect())
        connect.grid(row=1, column=2, padx=30, pady=10)
        #Configura el Toplevel en la pantalla.
        self.ConnectWindow.grid()


    #Funcion para connectarse al puerto seleccionado.
    def Connect(self):
        #Evalua si la seleccion actual esta vacia, si es valida abre el puerto con esa descripcion.
        if self.list.get(ACTIVE) == None:
            return 
        else:
            self.ser.port=self.portsDict[self.list.get(ACTIVE)]
        #Intenta abrir el puerto y validar el Arduino, de responder correctamente llama la subrutina y cierra la ventana.
        try:
            self.ser.open()
            if self.validateSerial() < 0:
                self.ConnectWindow.destroy()
                raise Exception("Arduino no validado") 
            else:
                messagebox.showinfo("Autentificacion satisfactoria","Mensaje de autentificacion validado correctamente")
                self.ConnectWindow.destroy()
        #De no poder abrir el puerto crea mensaje de alerta y cierra la ventana.
        except:
            messagebox.showerror("Puerto Serial no reconocido", "El puerto seleccionado no produce respuesta de autentificacion")
            self.ConnectWindow.destroy()


    #Funcion para desactivar botones
    def deactivate(self):
        self.bresume['state'] = "disabled"
        self.breport['state'] = "disabled"   


    #Funcion para activar botones
    def activate(self):
        self.bresume['state'] = "normal"
        self.breport['state'] = "normal"   

    #Funcion para pedir informacion al Arduino.
    def requestData(self):        
        #Limpia buffer, manda solicitud; lee y evalua respuesta, si es satiscatoria lee los datos y los regresa.
        
        self.ser.write(b'R')
        answer = self.ser.read().decode()
        if answer == 'E':            
            data = [float(self.ser.readline().decode('UTF-8')[:-2]) for x in range(4)]
            if "nan" in data:
                return 0
            return data
        return 0       


    #Funcion para pedir autorizacion.
    def validateSerial(self):
        count = 0
        #Limpia buffer, manda solicitud; lee, decodifica y evalua respuesta, si es satiscatoria retorna positivo.
        while True:
            ser.write(b'O')
            data = ser.read().decode()
            if data == 'K':
                break
            else:
                if count >3:
                    return -1
                
        return 1
    

    #Funcion para comenzar Hilo de espera.
    def threading(self):
        #Crea Hilo con la funcion esperando el valor del spinbox por una constante, inicia el hilo.
        self.fig1.clf()
        self.cs1.draw()
        self.fig2.clf()
        self.cs2.draw()
        self.t1=Thread(target=self.readFile, daemon=True)
        self.t1.start()


    #Funcion para actualizar datos.
    def updateGraph(self):
            

        #Limpia el contenedor de las graficas.
        self.fig1.clf()
        #Agrega las graficas al contenedor, las dibuja y configura en la pantalla.
        self.s1 = self.fig1.add_subplot(4, 1, 1, frameon=False).plot([x for x in range(len(self.sensorDat[0]))], self.sensorDat[0], 'b')
        self.s2 = self.fig1.add_subplot(4, 1, 2, frameon=False).plot([x for x in range(len(self.sensorDat[1]))], self.sensorDat[1], 'r')
        self.s3 = self.fig1.add_subplot(4, 1, 3, frameon=False).plot([x for x in range(len(self.sensorDat[2]))], self.sensorDat[2], 'g')
        self.cs1.draw()
        self.cs1.get_tk_widget().grid(row=0, column=1, rowspan=4, sticky=E)
        #Actualiza valores en Labels.    
        self.Accelx['text'] = str(self.sensorDat[0][-1])+"*"
        self.Accely['text'] = str(self.sensorDat[1][-1])+"*"
        self.Accelz['text'] = str(self.sensorDat[2][-1])+"*"


        self.fig2.clf()
        #Agrega las graficas al contenedor, las dibuja y configura en la pantalla.
        self.s4 = self.fig2.add_subplot(4, 1, 1, frameon=False).plot([x for x in range(len(self.sensorDat[3]))], self.sensorDat[3], 'b')
        self.s5 = self.fig2.add_subplot(4, 1, 2, frameon=False).plot([x for x in range(len(self.sensorDat[4]))], self.sensorDat[4], 'r')
        self.s6 = self.fig2.add_subplot(4, 1, 3, frameon=False).plot([x for x in range(len(self.sensorDat[5]))], self.sensorDat[5], 'g')
        self.cs2.draw()
        self.cs2.get_tk_widget().grid(row=0, column=1, rowspan=4, sticky=E)
        
        self.Gyrox['text'] = str(self.sensorDat[3][-1])+"*"
        self.Gyroy['text'] = str(self.sensorDat[4][-1])+"*"
        self.Gyroz['text'] = str(self.sensorDat[5][-1])+"*"
      

root = Tk()
s1 = IntVar()
s1.set(True)
s2 = IntVar()
s2.set(True)
s3 = IntVar()
s3.set(True)
s4 = IntVar()
s4.set(True)
dia = IntVar()
ddia = IntVar()
mes = IntVar()
mmes = IntVar()
anio = IntVar()

gui = UI(root,ser)
root.mainloop()