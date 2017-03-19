#!/usr/bin/env python
# -*- coding: utf-8 -*-
from framework.modulebase import Sensor
from framework.modulebase import Initializer
from subprocess import call
from pyspectator.computer import Computer
from framework.smartrest import SmartRESTMessage

class ComputerMonitoringSensor(Sensor, Initializer):
  xid = '/c8y-python-v0.1'

  def getSensorMessages(self):
    computer = Computer()
    with computer:
      temperature = computer.processor.temperature
      cpuload = computer.processor.load
      bytesSend = computer.network_interface.bytes_sent / 1000
      bytesReceived = computer.network_interface.bytes_recv / 1000
      freeMemory = computer.virtual_memory.available
      usedMemory = (computer.virtual_memory.total - freeMemory) / 1000
      freeMemory = freeMemory / 1000
      usedMemoryPercent = computer.virtual_memory.used_percent

    temperatureMsg = SmartRESTMessage('s/uc' + self.xid, 'M100', ['', temperature])
    cpuLoadMsg = SmartRESTMessage('s/uc' + self.xid, 'M101', ['', cpuload])
    trafficMsg = SmartRESTMessage('s/uc' + self.xid, 'M102', ['', bytesSend, bytesReceived])
    memoryMsg = SmartRESTMessage('s/uc' + self.xid, 'M103', ['', freeMemory, usedMemory, usedMemoryPercent])

    return [temperatureMsg, cpuLoadMsg, trafficMsg, memoryMsg]

  def getMessages(self):
    computer = Computer()
    with computer:
      name = str(computer.network_interface.name)
      mac = str(computer.network_interface.hardware_address)
      ip = str(computer.network_interface.ip_address)
      subnet = str(computer.network_interface.subnet_mask)

    networkMsg = SmartRESTMessage('s/uc' + self.xid, 'IU100', [self.serial, ip, mac, subnet, name, 1])

    return [networkMsg]
