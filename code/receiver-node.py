import os
import socket
import shutil
from bs4 import BeautifulSoup
import mysql.connector
#import xml.etree.ElementTree as ET
#from lxml import etree
for file in os.listdir("/home/log-transfer/incoming-logs/"):
    if file.endswith(".xml"):
        fileInput = open(file, "r")
        fileContent = fileInput.read()
        soup = BeautifulSoup(fileContent, "xml")
        machineName = str(soup.find('S', {'N': 'MachineName'}).string)
        eventID = int(soup.find('I32', {'N': 'EventID'}).string)
        eventSource = str(soup.find('S', {'N': 'Source'}).string)
        message = str(soup.find('S', {'N': 'Message'}).string)
        eventData = soup.find('Obj', {'N': 'EntryType'})
        eventLevel = int(eventData.findChildren('I32')[0].text)
        eventTime = str(soup.find('DT', {'N': 'TimeGenerated'}).string)
        log_guid = (file.split('$')[1].split('.')[0])
        #print(eventID)
        #print(message)
        #print(machineName)
        #print(eventLevel)
        #print(eventSource)
        #print(eventTime)
        #print(log_guid)

        #Check if SQL port is open on DB server before attempting transmit (src: stackoverflow)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('10.166.0.2',3306))
        #If DB connection is sucessful, insert the parsed data into the database
        if result == 0:
                #print "Port is open"
                db_connect = mysql.connector.connect(host="10.166.0.2",user="DBUSER",passwd="DBPASSWORD",database="DBNAME")
                db_cursor = db_connect.cursor()

                insert_command = "INSERT INTO DBNAME (log_guid, machine_name, event_src, event_id, event_level, event_msg, log_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                insert_data = (log_guid, machineName, eventSource, eventID, eventLevel, message, eventTime)
                #Check for any error during DB insert, if an error returns cancel the insert
                try:
                        db_cursor.execute(insert_command,insert_data)
                        db_connect.commit()
                        db_connect.close()
                        #print("insert ran")
                except:
                        db_connect.rollback()
                        db_connect.close()
                        #print("insert did not run")
        #If DB connection is not sucessful, exit the script.  It will reattempt on next cron run
        else:
                print "Port is not open"
                exit()
        #Once content was sucessfully entered into database, move current log file to archive folder
        moveTo='/home/log-transfer/incoming-logs/log-archives/'
        moveFrom='/home/log-transfer/incoming-logs/'
        shutil.move(moveFrom+file, moveTo)