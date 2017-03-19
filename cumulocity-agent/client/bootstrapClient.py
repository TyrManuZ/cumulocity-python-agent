#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging,platform,time,sys
import paho.mqtt.client as mqtt
from os.path import expanduser
import base64

class Bootstrap():
  bootstrapped = False

  def __init__(self, serial, path, configuration):
    self.serial = serial
    self.configuration = configuration
    self.url = self.configuration.getValue('mqtt', 'url')
    self.port = self.configuration.getValue('mqtt', 'port')
    self.ping = self.configuration.getValue('mqtt', 'ping.interval.seconds')

  def on_connect(self, client, userdata, flags, rc):
    logging.debug('Bootstrap connected with result code: '+str(rc))

  def on_message(self, client, userdata, msg):
    message = msg.payload.decode('utf-8')
    messageParts = message.split(',')
    logging.debug(messageParts)
    if messageParts[0] == '70':
      logging.debug('Storing credentials')
      self.configuration.writeCredentials(messageParts[1], messageParts[2], messageParts[3])
    self.bootstrapped = True

  def bootstrap(self):
    logging.debug('Start bootstrapping...')

    client = mqtt.Client(client_id=self.serial)
    client.on_message = self.on_message
    client.on_connect = self.on_connect

    credentials = self.configuration.getBootstrapCredentials()

    client.username_pw_set(credentials[0] + '/' + credentials[1], credentials[2])
    client.connect(self.url, int(self.port), int(self.ping))

    client.loop_start()
    client.subscribe('s/dcr')
    client.publish('s/ucr')

    while not self.bootstrapped:
      time.sleep(5)
      logging.debug('poll credentials')
      client.publish('s/ucr')

    client.disconnect()
    client.loop_stop()
