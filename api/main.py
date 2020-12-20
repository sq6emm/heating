#!/usr/bin/env python3

import logging, sys, time
from fastapi import FastAPI
from pyownet import protocol
from gpiozero import OutputDevice
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

app = FastAPI(
  title = "Heating API",
  description = " This is an API to Heating Controller",
  version = "beta"
)

req_temp = 5

sensorsdict = {}
sensorsdict['28.858D94050000'] = 'main.floor'
sensorsdict['28.B22793050000'] = 'main.wall'

def getTempOfSensor(sname):
  for i in readTemperature():
    if i.get('name') == sname:
      return float(i.get('temp'))

def readTemperature():
  sensorList = list()
  host, port = "localhost", 4304
  proxy = protocol.proxy(host, port)
  pid = int(proxy.read('/system/process/pid'))
  ver = proxy.read('/system/configuration/version').decode()
  for sensor in proxy.dir(slash=False, bus=False):
    stype = proxy.read(sensor + '/type').decode()
    if stype == "DS18B20":
      temp = float(proxy.read(sensor + '/temperature'))
      temp = "{0:.2f}".format(temp)
      sid = sensor.strip("/")
      if sid in sensorsdict:
        sname = sensorsdict[sid]
      else:
        sname = "unknown"
      sensorList.append({"id":sid, "name":sname, "temp":temp})
  return sensorList

def job():
  if getTempOfSensor("main.wall") < req_temp:
    print("powinnismy zaczac grzanie")

@app.get("/heating", tags=["heating"])
def get_heating():
  heatingList = list()
  sensorList = readTemperature()
#  mainheater = OutputDevice(25)
#  heatingList.append({"id":"gpio25","name":"main", "status":mainheater.value})
  return { "sensors": sensorList, "heaters": heatingList }

scheduler = BackgroundScheduler()
scheduler.add_job(job, 'interval', minutes=1)
scheduler.start()
