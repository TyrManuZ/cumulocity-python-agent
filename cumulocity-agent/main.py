#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform, time, sys, logging
from os.path import expanduser
from client.mqttClient import Agent
from client.bootstrapClient import Bootstrap
import utils.systemutils as utils
from utils.configutils import Configuration

if __name__ == '__main__':
  home = expanduser('~')
  path = home + '/.c8y-python'
  serial = utils.getSerial()
  config = Configuration(path)
  logging.basicConfig(filename=path + '/agent.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
  daemon = Agent(serial, path, config, path + '/agent.pid')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      print('Starting with serial: ' + utils.getSerial())
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.stop()
      print('Starting with serial: ' + utils.getSerial())
      daemon.start()
    elif 'debug' == sys.argv[1]:
      print('Starting debug with serial: ' + utils.getSerial())
      daemon.run()
    else:
      print('Unknown command')
      sys.exit(2)
    sys.exit(0)
  else:
    print('usage: %s start|stop|restart|debug' % sys.argv[0])
    sys.exit(2)
