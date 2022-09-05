from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
from time import sleep
from threading import Thread
import openpyxl
import pyrebase
from datetime import datetime,timedelta


import modulohuellas as huella

#import adafruit_fingerprint
#import serial

config = {
  "apiKey": "AIzaSyB6FncYkjm30o09qbsorZA2cjl0tJJQnCE",
  "authDomain": "proyecto-embebidos-g1.firebaseapp.com",
  "databaseURL": "https://proyecto-embebidos-g1-default-rtdb.firebaseio.com",
  "storageBucket": "proyecto-embebidos-g1.appspot.com"
}

firebase=pyrebase.initialize_app(config)
db=firebase.database()

#uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

#finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

lcd= LCD()
lectura=True
opcion=0
hora_entrada=datetime(2022,9,5,11,5)
hora_salida=datetime(2022,9,5,12,30)
usu="admin"
contra="123"

def safe_exit(signum, frame):
    exit(1)

signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)


def fecha():
	now = datetime.now()
	fecha_hora = now.strftime("%d/%m/%Y - %H:%M:%S")
	return fecha_hora		


def main():
    while lectura:
        ID=db.child("ID").get().val()
        lcd.clear()
        lcd.text("ELIJA NUMERO+ENTER",1)
        lcd.text("1. REGISTRO",2)
        lcd.text("2. MARCAR ASISTENCIA",3)
        lcd.text("3. PRESTAMO MATERIAL",4)
        opcion=str(input("ELIJA UNA OPCION"))
        if (opcion=="1"):
            lcd.clear()
            lcd.text("Ingrese su Nombre",1)
            lcd.text("    y Apellido",2)
            nombres=str(input("Ingrese su nombre y apellido"))
            lcd.clear()
            lcd.text("    Ingrese su",1)
            lcd.text("     Matricula",2)
            try:
                
                matricula=int(input("Ingrese su Matricula"))
                matricula=str(matricula)
                lcd.clear()
                lcd.text("    Ingrese su",1)
                lcd.text("     Paralelo",2)
                try:
                    paralelo=int(input("Ingrese su Paralelo"))
                    paralelo=str(paralelo)
                    data={"Nombres":nombres,"Matricula":matricula,"Paralelo":paralelo}
                    lcd.clear()
                    lcd.text("Verifique sus Datos",1)
                    lcd.text(nombres,2)
                    lcd.text(matricula,3)
                    lcd.text(paralelo,4)
                    sleep(7)#Se puede usar un input enter
                    lcd.clear()
                    lcd.text("Datos correctos",2)
                    lcd.text("S/N",3)
                    verificacion=str(input("Datos correctos S/N ")).lower()
                    if(verificacion=="s"):
                        if(huella.enroll_finger(ID)): 
                            db.child("Tabla Registro").child("ID:"+str(ID)).set(data)
                            ID=ID+1
                            db.child("ID").set(ID)
                        else:
                            lcd.clear()
                            lcd.text("Intentelo de nuevo",3) 
                            sleep(2)
                            #print("TERMINO OPCION1")
                    else:
                        print("Intentelo de nuevo")
                        lcd.clear()
                        lcd.text("Intentelo de nuevo",3) 
                        sleep(2)
                except ValueError:
                    lcd.clear()
                    lcd.text("Ingrese un valor",2)
                    lcd.text("     correcto",3)
                    sleep(2)
            except ValueError:
                lcd.clear()
                lcd.text("Ingrese un valor",2)
                lcd.text("     correcto",3)
                sleep(2)
            
        elif (opcion=="2"):
            lcd.clear()
            lcd.text("ELIJA NUMERO+ENTER",1)
            lcd.text("1. MARCAR ENTRADA",2)
            lcd.text("2. MARCAR SALIDA",3)
            opcion=str(input("ELIJA UNA OPCION"))
            if(opcion=="1"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    print("Detected #", dedoID)
                    lcd.clear()
                    lcd.text("Usuario Detectado",2)
                    now=datetime.now()
                    fecha_ing=str(now.strftime("%d/%m/%Y - %H:%M:%S"))
                    fecha1=str(now.strftime("%d-%m-%Y"))
                    fecha_dif=now-hora_entrada
                    f1=(fecha_dif.total_seconds())
                    t_max=60.0*10
                    t_max_atr=60.0*15
                    textID="ID:"+str(dedoID)
                    nombres=db.child("Tabla Registro").child(textID).child("Nombres").get().val()
                    matricula=db.child("Tabla Registro").child(textID).child("Matricula").get().val()
                    paralelo=db.child("Tabla Registro").child(textID).child("Paralelo").get().val()
                    estado=""
                    if(f1<=t_max):
                        print("Estado Asistio")
                        estado="Asistio"
                    elif(f1>t_max and f1<t_max_atr):
                        print("Estado Atrasado")
                        estado="Atrasado"
                    else:
                        estado="No Asistio"
                        print("Estado No Asistio")
                    data={"Nombres":nombres,"Matricula":matricula,"Paralelo":paralelo,"Fecha Ingreso":fecha_ing,"Fecha Salida":"","Estado":estado}
                    db.child("Tabla Asistencia").child(fecha1).child("ID:"+str(dedoID)).update(data)
                    
                    lcd.clear()
                    lcd.text("  INGRESO ENTRADA",2)
                    lcd.text("     CORRECTO",3)
                    sleep(2)
                else:
                    lcd.clear()
                    lcd.text("Error",2)
                    lcd.text("Intentelo de nuevo",3) 
                    sleep(2)
            elif(opcion=="2"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    textID="ID:"+str(dedoID)
                    print("Detected #", dedoID)
                    now=datetime.now()  
                    fecha1=str(now.strftime("%d-%m-%Y"))
                    ids=db.child("Tabla Asistencia").child(fecha1).shallow().get().val()
                    if (textID in ids):
                        lcd.clear()
                        lcd.text("Usuario Detectado",2)
                        fecha_sal=fecha()
                        db.child("Tabla Asistencia").child(fecha1).child(textID).child("Fecha Salida").set(fecha_sal)
                        print(fecha_sal)
                        lcd.clear()
                        lcd.text("  INGRESO SALIDA",2)
                        lcd.text("     CORRECTO",3)
                        sleep(2)
                    else:
                        lcd.clear()
                        lcd.text("NO SE HA MARCADO",2)
                        lcd.text("  EL INGRESO",3)
                        print("NO SE HA MARCADO EL INGRESO")
                        sleep(2)
            else:
                lcd.clear()
                lcd.text("OPCION INVALIDA",2)
                print("opcion invalida")
                sleep(2)
        elif (opcion=="3"):
            lcd.clear()
            lcd.text("ELIJA NUMERO+ENTER",1)
            lcd.text("1.PEDIR MATERIAL",2)
            lcd.text("2.DEVOLVER MATERIAL",3)
            opcion=str(input("ELIJA UNA OPCION"))
            if(opcion=="1"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    print("Detected #", dedoID)
                    lcd.clear()
                    lcd.text("USUARIO DETECTADO",2)
                    lcd.clear()
                    lcd.text("INGRESE NOMBRE",2)
                    lcd.text("DEL MATERIAL",3)
                    material=input("INGRESE NOMBRE DEL MATERIAL")
                    now=datetime.now()
                    fecha_pres=str(now.strftime("%d/%m/%Y - %H:%M:%S"))
                    textID="ID:"+str(dedoID)
                    nombres=db.child("Tabla Registro").child(textID).child("Nombres").get().val()
                    matricula=db.child("Tabla Registro").child(textID).child("Matricula").get().val()
                    paralelo=db.child("Tabla Registro").child(textID).child("Paralelo").get().val()
                    estado="NO DEVUELTO"
                    data={"Nombres":nombres,"Matricula":matricula,"Paralelo":paralelo}
                    lista={material:{"Fecha Prestamo":fecha_pres,"Fecha Devolucion":"","Estado":estado}}
                    lcd.clear()
                    lcd.text("Verifique los Datos",1)
                    lcd.text(nombres,2)
                    lcd.text(material,3)
                    sleep(5)#Se puede usar un input enter
                    lcd.clear()
                    lcd.text("Datos correctos",2)
                    lcd.text("S/N",3)
                    verificacion=str(input("Datos correctos S/N ")).lower()
                    if(verificacion=="s"):
                        db.child("Tabla Prestamo").child("ID:"+str(dedoID)).update(data)
                        db.child("Tabla Prestamo").child("ID:"+str(dedoID)).child("Lista Material").update(lista)
                        lcd.clear()
                        lcd.text("  PRESTAMO ",2)
                        lcd.text("  EXITOSO",3)
                        sleep(2)
                    else:
                        lcd.clear()
                        lcd.text("Intentelo de nuevo",2) 
                        sleep(2)
                else:
                    lcd.clear()
                    lcd.text("Error",2)
                    lcd.text("Intentelo de nuevo",3) 
                    sleep(2)
            elif(opcion=="2"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    textID="ID:"+str(dedoID)
                    ids=db.child("Tabla Prestamo").shallow().get().val()
                    if (textID in ids):
                        print("Detected #", dedoID)
                        lcd.clear()
                        lcd.text("USUARIO DETECTADO",2)
                        fecha_dev=fecha()
                        listam=db.child("Tabla Prestamo").child(textID).child("Lista Material").shallow().get().val()
                        listam=list(listam)
                        lcd.clear()
                        lcd.text("ELIJA NUMERO DE",1)
                        lcd.text("MATERIAL A",2)
                        lcd.text("DEVOLVER",3)
                        maximo=str(len(listam))
                        textlcd="1 a "+maximo
                        lcd.text(textlcd,4)
                        try:
                            opcion=int(input("ELIJA UN NUMERO"))
                            material_list=str(listam[opcion-1])
                            lcd.clear()
                            lcd.text("Verifique los Datos",1)
                            lcd.text("MATERIAL A DEVOLVER",2)
                            lcd.text(material_list,3)
                            sleep(5)
                            lcd.clear()
                            lcd.text("Datos correctos",2)
                            lcd.text("S/N",3)
                            verificacion=str(input("Datos correctos S/N ")).lower()
                            if(verificacion=="s"):
                                    db.child("Tabla Prestamo").child(textID).child("Lista Material").child(material_list).child("Fecha Devolucion").set(fecha_dev)
                                    db.child("Tabla Prestamo").child(textID).child("Lista Material").child(material_list).child("Estado").set("Devuelto")
                                    lcd.clear()
                                    lcd.text("  DEVOLUCION",2)
                                    lcd.text("  EXITOSA",3)
                                    sleep(2)
                            else:
                                lcd.clear()
                                lcd.text("Intentelo de nuevo",2) 
                                sleep(2)
                        
                        except ValueError:
                            lcd.clear()
                            lcd.text("Ingrese un valor",2)
                            lcd.text("     correcto",3)
                            sleep(2)
                        except IndexError:
                            lcd.clear()
                            lcd.text("Ingrese un valor",2)
                            lcd.text("     correcto",3)
                            sleep(2)     
                    else:
                        lcd.clear()
                        lcd.text("NO SE HA REALIZADO",2)
                        lcd.text("  PRESTAMO",3)
                        print("NO SE HA REALIZADO PRESTAMO")
                        sleep(2)
                    
            else:
                lcd.clear()
                lcd.text("OPCION INVALIDA",2)
                print("opcion invalida")    
                sleep(2)
        elif (opcion=="0"):
            lcd.clear()
            lcd.text("INGRESE USUARIO",2)
            usuario=str(input("ingrese usuario"))
            if(usuario==usu):
                lcd.clear()
                lcd.text("INGRESE CLAVE",2)
                clave=str(input("ingrese CLAVE"))
                if(clave==contra):
                    lcd.clear()
                    lcd.text("BIENVENIDO",1)
                    lcd.text("ESCOJA UNA OPCION",2)
                    lcd.text("1.BORRAR USUARIO",3)
                    lcd.text("2.GENERAR REPORTES",4)
                    opcion=str(input("ingrese opcion"))
                    if(opcion=="1"):
                        lcd.clear()
                        lcd.text("INGRESE NOMBRE Y",1)
                        lcd.text("APELLIDO DEL",2)
                        lcd.text("USUARIO",3)
                        usuario=str(input("ingrese nombres"))
                        ids=db.child("Tabla Registro").shallow().get().val()
                        ids=list(ids)
                        capa=len(ids)
                        
                        
                        n_estadom=[]
                        id_usu=0
                        for i in ids:
                            nombres=db.child("Tabla Registro").child(i).child("Nombres").get().val()
                            id_split=str(i)
                            id_split=i.split(":")
                            num=id_split[1]
                            num=int(num)
                            
                            if(usuario==nombres):
                                materiales=db.child("Tabla Prestamo").child(i).child("Lista Material").shallow().get().val()
                                materiales=list(materiales)
                                
                                for m in materiales:
                                    estado_m=db.child("Tabla Prestamo").child(i).child("Lista Material").child(m).child("Estado").get().val()
                                    n_estadom.append(estado_m)
                                id_usu=num
                            else:
                                lcd.clear()
                                lcd.text("POR FAVOR",2)
                                lcd.text("ESPERE",3)
                                print("por favor espere")
                        
                        n_materiales=len(n_estadom)       
                        devueltos=n_estadom.count("Devuelto")
                        
                        if(devueltos==n_materiales and n_materiales!=0):  
                            if huella.finger.delete_model(id_usu) == huella.adafruit_fingerprint.OK:
                                texto=str(id_usu)
                                i="ID:"+texto
                                print(i)
                                db.child("Tabla Registro").child(i).remove()
                                db.child("Tabla Prestamo").child(i).remove()
                                db.child("Tabla Reportes").child(i).remove()
                                fechas=db.child("Tabla Asistencia").shallow().get().val()
                                fechas=list(fechas)
                                for a in fechas:
                                    db.child("Tabla Asistencia").child(a).child(i).remove() 
                                print("USUARIO BORRADO!")
                                lcd.clear()
                                lcd.text("USUARIO BORRADO!",2)
                                sleep(2) 
                            else:
                                lcd.clear()
                                lcd.text("FALLO EN BORRAR",2)
                                print("FALLO EN BORRAR")
                                sleep(2)
                        if(devueltos<n_materiales and n_materiales!=0):
                            lcd.clear()
                            lcd.text("EL USUARIO DEBE",2)
                            lcd.text("DEVOLVER MATERIAL",3)
                            print("EL USUARIO DEBE DEVOLVER MATERIAL")
                            sleep(2)
                        
                        if(id_usu==0):
                            lcd.clear()
                            lcd.text("USUARIO NO",2)
                            lcd.text("ENCONTRADO",3)
                            print("USUARIO NO ENCONTRADO")
                            sleep(2)
                    elif(opcion=="2"):
                        ids=db.child("Tabla Registro").shallow().get().val()
                        ids=list(ids)
                        lista_fechas=[]
                        lcd.clear()
                        lcd.text("POR FAVOR ESPERE",2)
                        print("POR FAVOR ESPERE")
                        for i in ids:
                            fechas=db.child("Tabla Asistencia").shallow().get().val()
                            fechas=list(fechas)
                            lista_rep=[]
                            
                            for a in fechas:
                                if a not in lista_fechas:
                                    lista_fechas.append(a)
                                estado=db.child("Tabla Asistencia").child(a).child(i).child("Estado").get().val()
                                lista_rep.append(estado)
                            
                            asistencias=str(lista_rep.count("Asistio"))
                            atrasos=str(lista_rep.count("Atrasado"))
                            faltas=str(lista_rep.count("No Asistio"))
                            nombres=db.child("Tabla Registro").child(i).child("Nombres").get().val()
                            db.child("Tabla Reportes").child(i).child("Nombres").set(nombres)
                            db.child("Tabla Reportes").child(i).child("Asistencias").set(asistencias)
                            db.child("Tabla Reportes").child(i).child("Atrasos").set(atrasos)
                            db.child("Tabla Reportes").child(i).child("Faltas").set(faltas)
                            totaldias=len(lista_fechas)
                            sumadatos=int(asistencias)+int(faltas)+int(atrasos)
                            
                    
                            if (sumadatos<totaldias):
                                diferencia=totaldias-sumadatos
                                faltas=int(faltas)
                                faltas=faltas+diferencia
                                faltas=str(faltas)
                                db.child("Tabla Reportes").child(i).child("Faltas").set(faltas)
                        
                        
                        
                        wb=openpyxl.Workbook()
                        hoja=wb.active
                        ids=db.child("Tabla Reportes").shallow().get().val()
                        ids=list(ids)
                        hoja.append(("Asistencias","Atrasos","Faltas","Nombres"))
                        for i in ids:
                            reporteuwu=db.child("Tabla Reportes").child(i).shallow().get().val()
                            reporteuwu=list(reporteuwu)
                            data=[]
                            for u in reporteuwu:

                                datito=db.child("Tabla Reportes").child(i).child(u).get().val()
                                data.append(datito)
                            hoja.append(data)
                            
                        wb.save("Reportes.xlsx")
                        lcd.clear()
                        lcd.text("REPORTE GENERADO",2)
                        print("REPORTE GENERADO")
                        sleep(2)
                        
                    else:
                        lcd.clear()
                        lcd.text("OPCION INVALIDA",2)
                        print("opcion invalidaaaa")
                        sleep(2)
                else:
                    lcd.clear()
                    lcd.text("CLAVE INVALIDA",2)
                    print("CLAVE INVALIDA")
                    sleep(2)          
            else:
                lcd.clear()
                lcd.text("USUARIO INVALIDO",2)
                print("USUARIO INVALIDO")
                sleep(2)
                    
        else:
            lcd.clear()
            lcd.text("OPCION INVALIDA",2)
            print("opcion invalida")
            sleep(2)

try:
    #db.child("ID").set(1)#Solo se ejecuta una vez
    main()
except KeyboardInterrupt:
    lcd.clear()
    pass

finally:
    lectura=False
    sleep(0.5)
    lcd.clear()
