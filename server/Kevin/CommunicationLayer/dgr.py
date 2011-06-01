"""dgraminteface.py script

This program is intended to help inteface with an OMRON PLC as part
of the ELIXYS project.

"""

__author__ = "Kevin Quinn"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/05/03 18:40:00 $"


import socket
import time

HOST = "127.0.0.1"
PORT = 9600

ICF = "80"    #Info Ctrl Field - Binary 80 or 81 [1][0 =Cmd 1=Resp][00000][0 or 1=Resp Req]                      
RSV = "00"    #Reserved - Always Zero
GCT = "02"    #Gateway Count - Set to 02 (or do not set?!)
DNET = "00"   #Dest. Network - 00 (Local Network)
DNODE = "01"  #Dest. Node - Ethernet IP?
DUNIT = "00"  #Dest. Unit - 00=CPU FE=Ethernet
SNET = "00"   #Src. Net - 00 (Local Network)
SNODE = "02"  #Src. Node
SUNIT = "00"  #Src. Unit - 00=CPU
SVCID = "00"  #Service ID - 
PACKETINFO = [ICF,RSV,GCT,DNET,DNODE,DUNIT,SNET,SNODE,SUNIT,SVCID]

FINSHEADER = ["46","49","4E","53"]
FINSCLOSING = ["05", "01"]


#Dictionary of commands and the associaed codes.
CMD={"0101":"MEMORY AREA READ",
     "0102":"MEMORY AREA WRITE",
     "0103":"MEMORY AREA FILL",
     "0104":"MULTIPLE MEMORY AREA READ",
     "0105":"MEMORY AREA TRANSFER",
     "0201":"PARAMETER AREA READ",
     "0202":"PARAMETER AREA WRITE",
     "0203":"PARAMETER AREA CLEAR",
     "0306":"PROGRAM AREA READ",
     "0307":"PROGRAM AREA WRITE",
     "0308":"PROGRAM AREA CLEAR",
     "0401":"RUN",
     "0402":"STOP",
     "0501":"CPU UNIT DATA READ",
     "0502":"CONNECTION DATA READ",
     "0601":"CPU UNIT STATUS READ",
     "0620":"CYCLE TIME READ",
     "0701":"CLOCK READ",
     "0702":"CLOCK WRITE",
     "0920":"MESSAGE CLEAR",
     "0C01":"ACCESS RIGHT ACQUIRE",
     "0C02":"ACCESS RIGHT FORCED ACQUIRE",
     "0C03":"ACCESS RIGHT RELEASE",
     "2101":"ERROR CLEAR",
     "2102":"ERROR LOG READ",
     "2103":"ERROR LOG CLEAR",
     "2140":"FINS WRITE ACCESS LOG READ",
     "2141":"FINS WRITE ACCESS LOG CLEAR",
     "2201":"FILE NAME READ",
     "2202":"SINGLE FILE READ",
     "2203":"SINGLE FILE WRITE",
     "2204":"FILE MEMORY FORMAT",
     "2205":"FILE DELETE",
     "2207":"FILE COPY",
     "2208":"FILE NAME CHANGE",
     "220A":"MEMORY AREA FILE TRANSFER",
     "220B":"PARAMETER AREA FILE TRANS",
     "220C":"PROGRAM AREA FILE TRANSF",
     "2215":"CREATE/DELETE DIRECTORY",
     "2220":"MEMORY CASSETTE TRANSFER",
     "2301":"FORCED SET/RESET ",
     "2302":"FORCED SET/RESET CANCEL"}


mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def dance():
  #time.sleep(10)
  packet = ""
  for item in PACKETINFO:
    packet += item
  packet += "0102800000000001000"
  send = ""
  for each in range(16):
    send = (packet+hex(each)[2:])
    mySocket.sendto(send.decode("hex"),(HOST,PORT))
    print send[20:]
    time.sleep(0.05)
  for each in range(16,256):
    send = (packet[:-1]+hex(each)[2:])
    mySocket.sendto(send.decode("hex"),(HOST,PORT))
    print send[20:-1]
    time.sleep(0.05)
def constructPacket(packet):
  packetList = []
  packetList.extend(PACKETINFO)
  packetList.extend(packet)
  packet = ""
  for item in packetList:
    packet += item
  print ("\nSending packet: %s" % packet)
  if (CMD[packet[20:24]]):
    print ("Command: %s" % CMD[packet[20:24]])
  else:
    print ("Unknown command: %s" % packet[20:24])
  
  packet = packet.decode("hex")
  return packet
  
def deconstructPacket(packet):
  packet = packet[20:] #Strip header info
  print ("Recieved command: %s" % CMD[packet[:4]])
  if (getError(packet[4:8])):
    print ("Error: %s" % getError(packet[4:8]))
  if (len(packet)>=9):
    if ((packet[:4] == "0501") & (len(packet[:4]) >= 184)):#Get unit info
      packet = packet[8:] #Strip first 4 bytes
      print ("CPU Unit Model: %s" % packet[:40].decode("hex"))
      print ("CPU Version: v%s" % packet[40:60].decode("hex"))
      print ("Internal CPU Version: v%s" % packet[60:80].decode("hex"))
      print ("DIP Switch: %s" % int(packet[80:82],16))
      print ("Largest EM Bank #: Bank %s" % int(packet[82:84],16))#Next 36(72) are reserved
      print ("Program Area Size: %sKb" % int(packet[160:164],16))
      print ("IOM Size: %sKb" % int(packet[164:166],16))#[108:120].decode("hex")
      print ("Number of DM Words: %s Words" % int(packet[166:170],16))
      print ("Timer/Counter Size: %s" % (int(packet[170:172],16)*1024))
      print ("EM Size: %sKb" % (int(packet[172:174],16)*32))
      print ("Memory Card Size: %s" % int(packet[178:180],16))
      print ("Memory Card Type: %s" % int(packet[180:184],16))
      print ("CPU Bus Config: %s" % packet[184:])
    else:
      print ("Response data: %s" % packet[8:])

  
def getError(err):
  if (err[:2] == "00"):
    if (err == "0000"):
      err = None
    elif (err == "0001"):
      err = "Local node not in network."
  elif (err[:2] == "01"):
    if (err == "0102"):
      err = "Token timed out."
    elif (err == "0103"):
      err = "Retries failed."
    elif (err == "0104"):
      err = "Too many send frames."
    elif (err == "0105"):
      err = "Node address out of range."
    elif (err == "0106"):
      err = "Duplicate node address."
  elif (err[:2] == "02"):
    if (err == "0201"):
      err = "Destination node not in network."
    elif (err == "0202"):
      err = "Unit missing."
    elif (err == "0203"):
      err = "Third node missing."
    elif (err == "0204"):
      err = "Destination node busy."
    elif (err == "0205"):
      err = "Response timeout."
  elif (err[:2] == "03"):
    if (err == "0301"):
      err = "Communications controller error."
    elif (err == "0302"):
      err = "CPU unit error."
    elif (err == "0303"):
      err = "Controller error."
    elif (err == "0304"):
      err = "Unit number error."
  elif (err[:2] == "04"):
    if (err == "0401"):
      err = "Undefined command."
    elif (err == "0402"):
      err = "Not supported by model/version."
  elif (err[:2] == "05"):
    if (err == "0501"):
      err = "Destination setting address error."
    elif (err == "0502"):
      err = "No routing tables."
    elif (err == "0503"):
      err = "Routing table error."
    elif (err == "0504"):
      err = "Too many relays."
  elif (err[:2] == "10"):
    if (err == "1001"):
      err = "Command too long."
    elif (err == "1002"):
      err = "Command too short."
    elif (err == "1003"):
      err = "Elements/data don't match."
    elif (err == "1004"):
      err = "Command format error."
    elif (err == "1005"):
      err = "Header error."
  elif (err[:2] == "11"):
    if (err == "1101"):
      err = "Area classification missing."
    elif (err == "1102"):
      err = "Access size error."
    elif (err == "1103"):
      err = "Address range error."
    elif (err == "1104"):
      err = "Address range exceeded."
    elif (err == "1106"):
      err = "Program missing."
    elif (err == "1109"):
      err = "Relational error."
    elif (err == "110A"):
      err = "Duplicate data access."
    elif (err == "110B"):
      err = "Response too long."
    elif (err == "110C"):
      err = "Parameter error."
  elif (err[:2] == "20"):
    if (err == "2002"):
      err = "Protected."
    elif (err == "2003"):
      err = "Table missing."
    elif (err == "2004"):
      err = "Data missing."
    elif (err == "2005"):
      err = "Program missing."
    elif (err == "2006"):
      err = "File missing."
    elif (err == "2007"):
      err = "Data mismatch."
  elif (err[:2] == "21"):
    if (err == "2101"):
      err = "Read only."
    elif (err == "2102"):
      err = "Protected."
    elif (err == "2103"):
      err = "Cannot register."
    elif (err == "2105"):
      err = "Program missing."
    elif (err == "2106"):
      err = "File missing."
    elif (err == "2107"):
      err = "File already exists."
    elif (err == "2108"):
      err = "Cannot change."
  return err

def sendPacket():
  #mySocket.bind(('',PORT))
  print "Please enter a packet to send."
  print "Command format:[xxxx][xx][xxxxxx][xxxx]"
  print "ex. 0101800000020001"
  print "0101 - Read Memory Area" 
  print "0102 - Write Memory Area"
  print "0402 - STOP - puts system in program mode"
  print "0501 - Controller Read Data"
  print "0601 - Controller Read Status"
  print "0701 - Controller Read Clock"
  packet = raw_input( "Command to send:" )
  while (packet):
    data=None
    if (len(packet)%2 == 0):
      packet = constructPacket(packet)
      mySocket.sendto(packet,(HOST,PORT))
      print "\n"
      data = mySocket.recv(1024)
    if packet == "dance":
      dance()
    if packet == "end":
      break
    if data:
      deconstructPacket(data.encode("hex"))
      #print ("Recieved:%s from Client" % data.encode("hex"))
    packet = raw_input( "Command to send:" )
  print "Connection terminated."
  mySocket.close()

  
  
if __name__ == "__main__":
  sendPacket()