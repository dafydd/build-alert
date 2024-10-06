#!/usr/bin/python
 
alert_for_seconds = 30
after_breakage_resume_polling_after_seconds = 5 * 60
normal_poll_waiting_time = 2 * 60

host = 'example.com:8091'
path = '/alfred2/view/SomeProject/view/AgentJobs/api/json?pretty=true'

import httplib
import time
import random
import signal
from ctypes import *
import sys
import random
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, OutputChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit
 
 
def getInterfaceKit():
  try:
      interfaceKit = InterfaceKit()
      return interfaceKit
  except RuntimeError as e:
      print("Runtime Exception: %s" % e.details)
      print("Exiting....")
      exit(1)
 
def inferfaceKitAttached(e):
    attached = e.device
    print("InterfaceKit %i Attached!" % (attached.getSerialNum()))
 
def interfaceKitDetached(e):
    detached = e.device
    print("InterfaceKit %i Detached!" % (detached.getSerialNum()))
 
def interfaceKitError(e):
    try:
        source = e.device
        print("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
 
def initInterfaceKit(kit):
  try:
      kit.setOnAttachHandler(inferfaceKitAttached)
      kit.setOnDetachHandler(interfaceKitDetached)
      kit.setOnErrorhandler(interfaceKitError)
  except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
  print("Opening phidget object....")
  try:
      kit.openPhidget()
  except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
  try:
      kit.waitForAttach(10000)
  except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      try:
          kit.closePhidget()
      except PhidgetException as e:
          print("Phidget Exception %i: %s" % (e.code, e.details))
          print("Exiting....")
          exit(1)
      print("Exiting....")
      exit(1)

def closeInterfaceKit(kit):
  try:
      kit.closePhidget()
  except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
  print("Phidget Closed.")

def start_alarm(kit):
  print("Start Alarm")
  kit.setOutputState(0,True)

def stop_alarm(kit):
  print("Stop Alarm")
  kit.setOutputState(0,False)
 
def geturl(host,mthod,path):
  status  = 0 
  payload = ""
  try:
    c=httplib.HTTPConnection(host)
    c.request(mthod,path)
    r = c.getresponse()
    status = r.status
    payload = r.read()
  except Exception as err:
    return (0,"")
  return status,payload
 

def is_broken(source):
  return (source.find("\"red\"")!=-1)
   

k = getInterfaceKit()
initInterfaceKit(k)

def quit_without_alarm(signum, frame):
  print("Quitting...")
  stop_alarm(k)
  print("... issued stop.")
  closeInterfaceKit(k)
  exit(1)


def flashy_flash(signum, frame):
  print("Flashing...")
  for x in range(1,5):
    start_alarm(k)
    time.sleep(1)
    stop_alarm(k)
  print("... end flashing")

signal.signal(signal.SIGINT, quit_without_alarm)
signal.signal(signal.SIGUSR1, flashy_flash)

print("Starting polling loop")
while (True):
  print("polling...")
  result  = geturl(host,'GET',path)
  status  = result[0]
  payload = result[1]
  if status!=200:
    print("Failed to retrieve data. (Status %s)" % status)
  broken =  is_broken(payload)
  if broken:
    start_alarm(k)
    time.sleep(alert_for_seconds)
    stop_alarm(k)
    time.sleep(after_breakage_resume_polling_after_seconds)
  else:
    print("Not broken")
    time.sleep(normal_poll_waiting_time)
