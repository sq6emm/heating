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
  sensorsdict['28.B22793050000'] = 'main.floor'
  sensorsdict['28.858D94050000'] = 'main.wall'
  sensorList = list()
  heatingList = list()
  host, port = "localhost", 4304
  proxy = protocol.proxy(host, port)
  pid = int(proxy.read('/system/process/pid'))
  ver = proxy.read('/system/configuration/version').decode()
  for sensor in proxy.dir(slash=False, bus=False):
    stype = proxy.read(sensor + '/type').decode()
    if stype == "DS18B20":
      temp = float(proxy.read(sensor + '/temperature'))
      temp = "{0:.1f}".format(temp)
      sid = sensor.strip("/")
      if sid in sensorsdict:
        sname = sensorsdict[sid]
      else:
        sname = "unknown"
      sensorList.append({"id":sid, "name":sname, "temp":temp})
  mainheater = OutputDevice(25)
  heatingList.append({"id":"gpio25","name":"main", "status":mainheater.value})
  return { "sensors": sensorList, "heaters": heatingList }
