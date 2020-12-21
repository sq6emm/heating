#!/usr/bin/env python3

import logging, sys, time
from fastapi import FastAPI
from pydantic import BaseModel, conint
from typing import Optional
from enum import Enum
from pyownet import protocol
from gpiozero import DigitalOutputDevice
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

app = FastAPI(
  title = "Heating API",
  description = " This is an API to Heating Controller",
  version = "beta"
)

class HeatCmdEnum(str, Enum):
    on = 'on'
    off = 'off'

class Heat(BaseModel):
    heat_cmd: HeatCmdEnum
    heat_temp_warm: conint(ge=18, le=25) = None
    heat_temp_freeze: conint(ge=0, le=10) = None

heat_cmd = "off"
heat_temp_freeze = 5
heat_temp_warm = 21

mainheater = DigitalOutputDevice(25)
mainheater.off()

sensorsdict = {}
sensorsdict['28.858D94050000'] = 'main.floor'
sensorsdict['28.B22793050000'] = 'main.wall'

def getTempOfSensor(sname):
  for i in readSensorsTemp():
    if i.get('name') == sname:
      return float(i.get('temp'))

def readSensorsTemp():
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

def readHeating():
  heatingList = list()
  if mainheater.value == 0: main_heater="off"
  if mainheater.value == 1: main_heater="on"
  heatingList.append({"id":"gpio25","name":"main", "status":main_heater})
  return heatingList

def readSettings():
  settingsList = list()
  settingsList = {"heat_cmd":heat_cmd,"heat_temp_warm":heat_temp_warm, "heat_temp_freeze":heat_temp_freeze}
  return settingsList

def job():
  if heat_cmd == "on":
    if getTempOfSensor("main.wall") < heat_temp_warm:
      mainheater.on()
    else:
      mainheater.off()
  else:
    if getTempOfSensor("main.floor") < heat_temp_freeze:
      mainheater.on()
    else:
      mainheater.off()

@app.get("/heating", tags=["heating"])
def get_heating():
  sensorList = readSensorsTemp()
  heatingList = readHeating()
  settingsList = readSettings()
  return { "settings": settingsList, "sensors": sensorList, "heaters": heatingList }

@app.post("/heating", tags=["heating"])
def post_heating(heat: Heat):
  global heat_cmd, heat_temp_warm, heat_temp_freeze
  if heat.heat_cmd: heat_cmd = heat.heat_cmd
  if heat.heat_temp_warm: heat_temp_warm = heat.heat_temp_warm
  if heat.heat_temp_freeze: heat_temp_warm = heat.heat_temp_freeze
  job()
  sensorList = readSensorsTemp()
  heatingList = readHeating()
  settingsList = readSettings()
  return { "settings": settingsList, "sensors": sensorList, "heaters": heatingList }

scheduler = BackgroundScheduler()
scheduler.add_job(job, 'interval', minutes=5)
scheduler.start()
