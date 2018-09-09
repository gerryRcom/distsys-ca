import os
import socket
from bs4 import BeautifulSoup
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
        print(eventID.string)
        print(message.string)
        print(machineName.string)
        print(eventLevel[0].text)
        print(eventSource.string)
        print(eventTime.string)

#Check if SQL port is open on DB server before attempting transmit (src: stackoverflow)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex(('db-master.gerryr.com',3306))
if result == 0:
        print "Port is open"
else:
        print "Port is not open"