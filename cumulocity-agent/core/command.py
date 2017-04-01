#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, time
from framework.modulebase import Listener
from framework.smartrest import SmartRESTMessage

class CommandHandler(Listener):

  availableCommands = ['set', 'get']


  def __init__(self, serial, agent, configuration):
    self.configuration = configuration
    self.agent = agent
    self.serial = serial
    self.commandMap = {
      'set': self.executeSet,
      'get': self.executeGet
    }

  def handleOperation(self, message):
    if 's/ds' in message.topic and message.messageId == '511':
      executing = SmartRESTMessage('s/us', '501', ['c8y_Command'])
      self.agent.publishMessage(executing)
      fullCommand = message.values[1]
      commandParts = fullCommand.split()
      if commandParts[0] not in self.availableCommands:
        result = SmartRESTMessage('s/us', '502', ['c8y_Command', "\"Unknown command: '" + commandParts[0] + "'\""])
      else:
        result = self.commandMap[commandParts[0]](commandParts[1:])
      self.agent.publishMessage(result)

  def getSupportedOperations(self):
    return ['c8y_Command']

  def getSupportedTemplates(self):
    return []

  def executeSet(self, parts):
    if len(parts) is 3:
      if parts[0] == 'secret':
        return SmartRESTMessage('s/us', '502', ['c8y_Command', "Cannot change 'secret' category"])
      self.configuration.setValue(parts[0], parts[1], parts[2])
      return SmartRESTMessage('s/us', '503', ['c8y_Command', '[' + parts[0] + '][' + parts[1] + '] = ' + parts[2]])
    else:
      return SmartRESTMessage('s/us', '502', ['c8y_Command', "'set' command expects '<category> <key> <value>'"])

  def executeGet(self, parts):
    if len(parts) is 2:
      if parts[0] == 'secret':
        return SmartRESTMessage('s/us', '502', ['c8y_Command', "Cannot read 'secret' category"])
      result = self.configuration.getValue(parts[0], parts[1])
      if result is None:
        return SmartRESTMessage('s/us', '502', ['c8y_Command', "category/key not found"])
      return SmartRESTMessage('s/us', '503', ['c8y_Command', '[' + parts[0] + '][' + parts[1] + '] = ' + result])
    else:
      return SmartRESTMessage('s/us', '502', ['c8y_Command', "'get' command expects '<category> <key>'"])
