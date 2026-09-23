# Base of Date to Clients

#First I need to do a Base of Date in SQLite
#to solve a basic problem of serching and access
#Primero necesito hacer la Base de Datos en SQLite
#para resolver un problema básico de busqueda y acceso

import sqlite3
con = sqlite3.connect("Base_of_Date.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS Clients "
            "(name_costumer TEXT, dni INTEGER)")
cur.execute("INSERT INTO Clients VALUES (?,?)", (
            (input("Welcome, insert your Address and Name: "), (int(input("Insert your DNI: "))))))
con.commit()

#Now it's important make an ID automatic generator for be able to
#storage the information of every costumer log_in in the Online Store
#and print the results to check it
#It's not necesary the print...
#Ahora es importante hacer un generador automatico de ID para poder
#almacenar la información de cada cliente que inicie sesión en la Tienda Online
#e imprimir los resultados para revisarlos
#No es necesario la impresión...

for fila in cur.execute("SELECT *FROM Clients"):
    print(fila)
