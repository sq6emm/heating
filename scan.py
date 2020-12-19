#!/usr/bin/env python3

from pyownet import protocol
from gpiozero import OutputDevice

def sensors():
  sensorsdict = {}
  sensorsdict['/28.B22793050000'] = 'podloga'
  sensorsdict['/28.858D94050000'] = 'sciana'

  host, port = "localhost", 4304
  proxy = protocol.proxy(host, port)
  pid = int(proxy.read('/system/process/pid'))
  ver = proxy.read('/system/configuration/version').decode()
  for sensor in proxy.dir(slash=False, bus=False):
    stype = proxy.read(sensor + '/type').decode()
    if stype == "DS18B20":
      temp = float(proxy.read(sensor + '/temperature'))
      temp = "{0:.1f}".format(temp)
      print(sensorsdict[sensor], sensor, temp)

def heating():
  mainheater = OutputDevice(25)
  print(str(mainheater.value))

if __name__ == '__main__':
    sensors()
    heating()
