#!/usr/bin/env python3

import logging, sys
from fastapi import FastAPI
from pyownet import protocol
from gpiozero import OutputDevice

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

app = FastAPI(
  title = "Heating API",
  description = " This is an API to Heating Controller",
  version = "beta"
)

@app.get("/heating", tags=["heating"])
def get_heating():
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
      return sensorsdict
  mainheater = OutputDevice(25)
  print(str(mainheater.value))
