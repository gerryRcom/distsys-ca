import os
import socket
from bs4 import BeautifulSoup
import mysql.connector
#import xml.etree.ElementTree as ET
#from lxml import etree
for file in os.listdir("/home/log-transfer/incoming-logs/"):
    if file.endswith(".xml"):
        fileInput = open(file, "r")
        fileContent = fileInput.read()
        soup = BeautifulSoup(fileContent, "xml")
        machineName = soup.find('S', {'N': 'MachineName'})
        eventID = soup.find('I32', {'N': 'EventID'})
        eventSource = soup.find('S', {'N': 'Source'})
        message = soup.find('S', {'N': 'Message'})
        eventData = soup.find('Obj', {'N': 'EntryType'})
        eventLevel = eventData.findChildren('I32')
        eventTime = soup.find('DT', {'N': 'TimeGenerated'})
        log_guid = (file.split('$')[1].split('.')[0])
        print(eventID.string)
        print(message.string)
        print(machineName.string)
        print(eventLevel[0].text)
        print(eventSource.string)
        print(eventTime.string)
        print(log_guid)

#Check if SQL port is open on DB server before attempting transmit (src: stackoverflow)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex(('SERVER',3306))
if result == 0:
        print "Port is open"
        db_connect = mysql.connector.connect(host="SERVER",user="ENTERUSER",passwd="ENTERPASSWORD",database="DATABASENAME")
        db_cursor = db_connect.cursor()

        insert_command = "INSERT INTO log_data (log_guid, machine_name, event_src, event_id, event_level, event_msg) VALUES (%s, %s, %s, %s, %s, %s)"
        insert_data = (log_guid, machineName.string, eventSource.string, int(eventID.string), int(eventLevel[0].text), message.string)
        #try:
        db_cursor.execute(insert_command,insert_data)
        db_connect.comit()
        db_connect.close()
        print("insert ran")
        #except:
        #       db_connect.rollback()
        #       db_connect.close()
        #       print("insert did not run")
#else:
        print "Port is not open"
        exit()
