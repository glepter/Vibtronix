from machine import Pin
from machine import SoftI2C
import time
import network
import socket
import mpu6050

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SSID = "Totalplay-EEA7"
password = 'EEA7506Es9Jd3Tbj'
serverAddr = "192.168.100.61"
server_port = 12345




# Initialize Wi-Fi
sta_if = network.WLAN(network.STA_IF)
print("Connecting to: "+SSID)
sta_if.active(True)
sta_if.connect(SSID, password)
while not sta_if.isconnected():
  print("intentando...")
  time.sleep(2)

i2c = SoftI2C(scl = Pin(9), sda = Pin(8))

count = 0

mpu = mpu6050.accel(i2c)


ax = [0,0,0,0,0,0,0,0,0,0]
ay = [0,0,0,0,0,0,0,0,0,0]
az = [0,0,0,0,0,0,0,0,0,0]

gx = [0,0,0,0,0,0,0,0,0,0]
gy = [0,0,0,0,0,0,0,0,0,0]
gz = [0,0,0,0,0,0,0,0,0,0]

xp = 0
yp = 0
zp = 0
xg = 0
yg = 0
zg = 0


while True:
  print(count)
  temps = (mpu.get_values())


  acz = temps["AcZ"]
  acy = temps["AcY"]
  acx = temps["AcX"]
  gyz = temps["AcZ"]
  gyy = temps["AcY"]
  gyx = temps["AcX"]

  if(count<10):
    ax[count] = acx
    ay[count] = acy
    az[count] = acz
    gx[count] = gyx
    gy[count] = gyy
    gz[count] = gyz

  else:
    ax[0:8] = ax[1:9]
    ax[9] = acx
    ay[0:8] = ay[1:9]
    ay[9] = acy
    az[0:8] = az[1:9]
    az[9] = acz

    gx[0:8] = gx[1:9]
    gx[9] = gyx
    gy[0:8] = gy[1:9]
    gy[9] = gyy
    gz[0:8] = gz[1:9]
    gz[9] = gyz


    xp = (ax[0]+ax[1]+ax[2]+ax[3]+ax[4]+ax[5]+ax[6]+ax[7]+ax[8]+ax[9])/10
    yp = (ay[0]+ay[1]+ay[2]+ay[3]+ay[4]+ay[5]+ay[6]+ay[7]+ay[8]+ay[9])/10
    zp = (az[0]+az[1]+az[2]+az[3]+az[4]+az[5]+az[6]+az[7]+az[8]+az[9])/10

    xg = (gx[0]+gx[1]+gx[2]+gx[3]+gx[4]+gx[5]+gx[6]+gx[7]+gx[8]+gx[9])/10
    yg = (gy[0]+gy[1]+gy[2]+gy[3]+gy[4]+gy[5]+gy[6]+gy[7]+gy[8]+gy[9])/10
    zg = (gz[0]+gz[1]+gz[2]+gz[3]+gz[4]+gz[5]+gz[6]+gz[7]+gz[8]+gz[9])/10
  
  print("ac X: ",xp, "    ac X:",yp, "    ac X:",zp,"    g X: ",xg, "    g Y:",yg, "    g z:",zg)
  

  new = xp,yp,zp,xg,yg,zg

  sock.sendto(str(new).encode(), (serverAddr, server_port))
  count += 1
  
  time.sleep(0.1)
  
