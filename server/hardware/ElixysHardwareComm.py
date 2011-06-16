""" ElixysHardwareComm.py

Implements the HardwareComm interface for the Elixys hardware

"""

# Imports
import socket
import time
from configobj import ConfigObj

class HardwareComm:
    ### Construction ###
    def __init__(self):
        # Load the hardware map and robot positions
        self.__pHardwareMap = ConfigObj("ElixysHardwareMap.ini")
        self.__pRobotPositions = ConfigObj("ElixysRobotPositions.ini")

    ### Public functions ###

    # Startup/shutdown
    def StartUp(self, bResetSystem = True):
        pass
    def ShutDown(self):
        pass

    # Valves
    def OpenValve(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName, True)
    def CloseValve(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName, False)

    # Vacuum system
    def VacuumSystemOn(self):
        self.__SetBinaryValue("VacuumSystemOn", True)
    def VacuumSystemOff(self):
        self.__SetBinaryValue("VacuumSystemOn", False)

    # Cooling system
    def CoolingSystemOn(self):
        self.__SetBinaryValue("CoolingSystemOn", True)
    def CoolingSystemOff(self):
        self.__SetBinaryValue("CoolingSystemOn", False)

    # Pressure regulator
    def PressureRegulatorOn(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_On", True)
    def PressureRegulatorOff(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_On", False)
    def SetPressureRegulatorPressure(self, sHardwareName, fPressure):
        pass

    # Reagent robot motion
    def MoveReagentRobotToPosition(self, sPositionName):
        pPosition = self.__LookUpRobotPosition(sPositionName)
        self.__MoveToAbsolutePosition("ReagentRobot_SetX", pPosition["x"])
        self.__MoveToAbsolutePosition("ReagentRobot_SetZ", pPosition["z"])
    def GripperUp(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", True)
    def GripperDown(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", False)
    def GripperOpen(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", True)
    def GripperClose(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", False)

    # Reactor motion
    def MoveReactorToPosition(self, sPositionName):
        pPosition = self.__LookUpRobotPosition(sPositionName)
        sReactor = sPositionName.split("_")[0]
        self.__MoveToAbsolutePosition(sReactor + "_SetZ", pPosition["z"])
    def ReactorUp(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetReactorUp", True)
    def ReactorDown(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetReactorUp", False)

    # Temperature controllers
    def HeaterOn(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetHeaterOn", True)
    def HeaterOff(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetHeaterOn", False)
    def SetHeaterSetPoint(self, sHardwareName, fSetPoint):
        pass

    # Stir motor
    def SetMotorSpeed(self, sHardwareName, nMotorSpeed):
        pass

    # Radiation detector
    def ReadRadiationDetector(self):
        pass


    ### Private functions ###

    # Look up hardware name details
    def __LookUpHardwareName(self, sHardwareName):
        try:
            # Extract the hardware descriptor string
            pHardwareNameComponents = sHardwareName.split("_")
            if len(pHardwareNameComponents) == 1:
                sHardwareDescriptor = str(self.__pHardwareMap[pHardwareNameComponents[0]])
            elif len(pHardwareNameComponents) == 2:
                sHardwareDescriptor = str(self.__pHardwareMap[pHardwareNameComponents[0]][pHardwareNameComponents[1]])
            elif len(pHardwareNameComponents) == 3:
                sHardwareDescriptor = str(self.__pHardwareMap[pHardwareNameComponents[0]][pHardwareNameComponents[1]][pHardwareNameComponents[2]])
            else:
                raise Exception()

            # Convert the descriptor string to a dictionary object
            pDescriptorComponents = sHardwareDescriptor.split(".")
            if len(pDescriptorComponents) != 3:
                raise Exception()
            return {"name":sHardwareName,
                "type":str(pDescriptorComponents[0]),
                "access":str(pDescriptorComponents[1]),
                "location":str(pDescriptorComponents[2])}
        except Exception as ex:
            # Raise an appropriate error
            raise Exception("Failed to look up hardware name: " + str(sHardwareName))

    # Look up robot position
    def __LookUpRobotPosition(self, sPositionName):
        try:
            # Extract the robot position descriptor string
            pPositionNameComponents = sPositionName.split("_")
            if len(pPositionNameComponents) == 1:
                sPositionDescriptor = str(self.__pRobotPositions[pPositionNameComponents[0]])
            elif len(pPositionNameComponents) == 2:
                sPositionDescriptor = str(self.__pRobotPositions[pPositionNameComponents[0]][pPositionNameComponents[1]])
            else:
                raise Exception()

            # Convert the descriptor string to a dictionary object
            pDescriptorComponents = sPositionDescriptor.split("_")
            if len(pDescriptorComponents) == 1:
                return {"name":sPositionName,
                    "z":str(pDescriptorComponents[0])}
            elif len(pDescriptorComponents) == 2:
                return {"name":sPositionName,
                    "x":str(pDescriptorComponents[0]),
                    "z":str(pDescriptorComponents[1])}
            else:
                raise Exception()
        except Exception as ex:
            # Raise an appropriate error
            raise Exception("Failed to look up robot position: " + str(sPositionName))

    # Move robot to absolute position
    def __MoveToAbsolutePosition(self, sHardwareName, nAbsolutePosition):
        print "Implement MoveToAbsolutePosition (" + sHardwareName + " = " + str(nAbsolutePosition) + ")"

    # Set binary value
    def __SetBinaryValue(self, sHardwareName, bValue):
        print "Implement SetBinaryValue (" + sHardwareName + " = " + str(self.__LookUpHardwareName(sHardwareName)) + ")"

    # Set analog value
    def __SetAnalogValue(self, sHardwareName, fValue):
        print "Implement SetAnalogValue (" + sHardwareName + ")"




    def __ConstructPacket(self, packet):
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
    def __DeconstructPacket(self, packet):
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
    def __GetError(self, err):
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
    def __SendPacket(self):
      mySocket.bind(('',PORT))
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

    # Updating thread
    def __UpdatingThread():
        pass

    # Receiving thread
    def ReceivingThread():
        pass

    ### Member variables ###

    # IP and port of the PLC
    HOST = "192.168.250.1"
    PORT = 9600

    # Constants for PLC command formatting
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

# Main function for testing the Elixys hardware communication
if __name__ == "__main__":
    pHardwareComm = HardwareComm()
    pHardwareComm.StartUp();

    pHardwareComm.OpenValve("Reactor1_EvaporationValve")
    pHardwareComm.OpenValve("Reactor1_VacuumValve")
    pHardwareComm.CloseValve("Reactor1_EvaporationValve")
    pHardwareComm.CloseValve("Reactor1_VacuumValve")

    pHardwareComm.VacuumSystemOn()
    pHardwareComm.CoolingSystemOff()
    pHardwareComm.PressureRegulatorOn("PressureRegulator1")

    pHardwareComm.MoveReagentRobotToPosition("Reactor1_Reagent5")
    pHardwareComm.GripperDown()
    pHardwareComm.GripperClose()
    pHardwareComm.GripperUp()
    pHardwareComm.MoveReagentRobotToPosition("Reactor1_ReagentDelivery1")
    pHardwareComm.GripperDown()

    pHardwareComm.ReactorDown("Reactor1")
    pHardwareComm.MoveReactorToPosition("Reactor1_Transfer")
    pHardwareComm.ReactorUp("Reactor1")

    pHardwareComm.HeaterOn("Reactor1_TemperatureController1")
    pHardwareComm.SetHeaterSetPoint("Reactor1_TemperatureController1", 140.0)
    pHardwareComm.HeaterOff("Reactor1_TemperatureController1")

    pHardwareComm.SetMotorSpeed("Reactor1", 500)

    pHardwareComm.ReadRadiationDetector()

    pHardwareComm.ShutDown()
