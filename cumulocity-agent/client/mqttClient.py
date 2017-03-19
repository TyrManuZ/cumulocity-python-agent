#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, platform, time, sys
import paho.mqtt.client as mqtt
from os.path import expanduser
from daemon import Daemon
from client.bootstrapClient import Bootstrap
import utils.moduleloader as moduleloader
from framework.smartrest import SmartRESTMessage

class Agent(Daemon):
  __sensors = []
  __listeners = []
  __supportedOperations = set()
  __supportedTemplates = set()

  def __init__(self, serial, path, configuration, pidfile):
    self.serial = serial
    self.configuration = configuration
    self.pidfile = pidfile
    self.path = path
    self.url = self.configuration.getValue('mqtt', 'url')
    self.port = self.configuration.getValue('mqtt', 'port')
    self.ping = self.configuration.getValue('mqtt', 'ping.interval.seconds')
    self.interval = int(self.configuration.getValue('agent', 'main.loop.interval.seconds'))

  def __on_connect(self, client, userdata, flags, rc):
    logging.debug('Agent connected with result code: '+str(rc))

  def __on_message(self, client, userdata, msg):
    decoded = msg.payload.decode('utf-8')
    messageParts = decoded.split(',')
    message = SmartRESTMessage(msg.topic, messageParts[0], messageParts[1:])
    logging.debug('Received: topic=%s msg=%s', message.topic, message.getMessage())
    for listener in self.__listeners:
      listener.handleOperation(message)

  def publishMessage(self, message):
    logging.debug('Send: topic=%s msg=%s', message.topic, message.getMessage())
    self.__client.publish(message.topic, message.getMessage())

  def run(self):
    logging.info('Starting agent')

    credentials = self.configuration.getCredentials()
    logging.debug('Credentials:')
    logging.debug(credentials)
    if credentials is None:
      logging.info('No credentials found. Starting bootstrap mode.')
      bootstrapCredentials = self.configuration.getBootstrapCredentials()
      if bootstrapCredentials is None:
        logging.error('No bootstrap credentials found. Stopping agent.')
        return
      bootstrapAgent = Bootstrap(self.serial, self.path, self.configuration)
      bootstrapAgent.bootstrap()
      credentials = self.configuration.getCredentials()

    if credentials is None:
      logging.error('No credentials found after bootstrapping. Stopping agent.')
      return

    self.__client = mqtt.Client(self.serial)
    self.__client.on_connect = self.__on_connect
    self.__client.on_message = self.__on_message

    self.__client.username_pw_set(credentials[0] + '/' + credentials[1], credentials[2])
    self.__client.connect(self.url, int(self.port), int(self.ping))

    self.__client.loop_start()
    self.__client.subscribe('s/e')
    self.__client.subscribe('s/ds')

    # Load modules
    modules = moduleloader.findAgentModules()
    classCache = {}

    for sensor in modules['sensors']:
      currentSensor = sensor(self.serial)
      classCache[sensor.__name__] = currentSensor
      self.__sensors.append(currentSensor)
    for listener in modules['listeners']:
      if listener.__name__ in classCache:
        currentListener = classCache[listener.__name__]
      else:
        currentListener = listener(self.serial, self)
        classCache[listener.__name__] = currentListener
      supportedOperations = currentListener.getSupportedOperations()
      supportedTemplates = currentListener.getSupportedTemplates()
      if supportedOperations is not None:
        self.__supportedOperations.update(supportedOperations)
      if supportedTemplates is not None:
        self.__supportedTemplates.update(supportedTemplates)
      self.__listeners.append(currentListener)
    for initializer in modules['initializers']:
      if initializer.__name__ in classCache:
        currentInitializer = classCache[initializer.__name__]
      else:
        currentInitializer = initializer(self.serial)
        classCache[listener.__name__] = currentInitializer
      messages = currentInitializer.getMessages()
      if messages is None or len(messages) == 0:
        continue
      for message in messages:
        logging.debug('Send topic: %s, msg: %s', message.topic, message.getMessage())
        self.__client.publish(message.topic, message.getMessage())

    classCache = None

    # set supported operations
    logging.info('Supported operations:')
    logging.info(self.__supportedOperations)
    supportedOperationsMsg = SmartRESTMessage('s/us', 114, self.__supportedOperations)
    self.publishMessage(supportedOperationsMsg)

    # subscribe additional topics
    for xid in self.__supportedTemplates:
      logging.info('Subscribing to XID: %s', xid)
      self.__client.subscribe('s/dc/' + xid)

    while True:
      time.sleep(self.interval)
      for sensor in self.__sensors:
        messages = sensor.getSensorMessages()
        if messages is None or len(messages) == 0:
          continue
        for message in messages:
          self.publishMessage(message)
