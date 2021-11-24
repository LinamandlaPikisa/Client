import socket
import time
import threading
from datetime import datetime
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

def setup():
#setting up the pi connection

   global IP, port, sock, temp, ldr, send, lastSample
    
   spi = busio.SPI(clock = board.SCK, MISO = board.MISO, MOSI = board.MOSI)
   cs  = digitalio.DigitalInOut(board.D5)
   mcp  = MCP.MCP3008(spi, cs)
   temp = AnalogIn(mcp, MCP.P1)
   ldr = AnalogIn(mcp, MCP.P2)
   
#enabling connection   
   
   IP = '192.168.43.100'
   port = 1234
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.connect((IP, port))
   
   send = False
   lastSample = ""
   
   sample()

#this handles messages received from the server
   
   while(True):
   
      
      d = sock.recv(1024)
      d = d.decode("utf-8")
      
      #when the message is sensor off you stop sampling
      if d == "SensorOff":
         send = False
      
      #when the message is sensor on you start sampling
      elif d == "SensorOn":
         send = True
      
      #when the message is status then you send to the server the status of whether the client is sampling or not
      elif d == "Status":
         
         if(send):
            message = "Status: Active , Last Sample Time: " + lastSample
            sock.sendall(str.encode(message))
         else:
            message = "Status: Not Active , Last Sample Time: " + lastSample
            sock.sendall(str.encode(message))
            
      elif d == "Exit":
         send = False      
               
      time.sleep(5)
      
def sample():

   global sock, lastSample, send
   
   thread = threading.Timer(10, sample)
   thread.start();
   
   if(send):
      #reading data from the sensors
      tempR = temp.value
      tempC = round((tempR - 0.5)*100,3)
      ldrR = ldr.value
         
      lastSample = str(datetime.now().time())[0:8]
      data = datetime.now().date().strftime("%d:%m:%y")+";"+ lastSample+ ";"+ str(ldrR)+ ";"+str(tempR)+";"+str(tempC)
         
      #sending the data to the server
      sock.sendall(str.encode(data))
        
 
if __name__ == '__main__':
   setup()
   