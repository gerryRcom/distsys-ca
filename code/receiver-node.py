import os
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