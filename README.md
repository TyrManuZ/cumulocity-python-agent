# Cumulocity MQTT Python agent
A simple python agent connecting to Cumulocity via MQTT

# Prerequisites
1. Install python 3.x
2. Install libraries from requirements.txt
3. Create a folder ".c8y-agent" in your home directory and copy the agent.ini from the config folder there
4. Set the correct bootstrap password (If you do not know it ask support@cumulocity.com)
5. Upload the smartrest.json to the SmartREST templates in your tenant (you can use the import functionality)

# Running the agent
The agent can be started
    
    python main.py start
    
stopped

    python main.py stop
    
and restarted

    python main.py restart
    
You can also run the agent with debug which will not create the daemon and run it in the process directly

    python main.py debug

# Bootstrapping

The agent uses normal device bootstrap. The serial that is used for bootstrapping is printed at the start of the agent.
The credentials are later stored in the agent.ini file. To re-register the agent to a different tenant you can simply delete those lines.
# Extending the agent

The agent knows three types of classes that it will automatically load and include from the "agentmodules" directory.

1. Sensors

        class Sensor:
          __metaclass__ = ABCMeta

          def __init__(self, serial):
            self.serial = serial

          '''
          Returns a list of SmartREST messages. Will be called every iteration of the main loop.
          '''
          @abstractmethod
          def getSensorMessages(self): pass
      
    Sensors are periodically polled by the main loop and published.

2. Listeners

        class Listener:
          __metaclass__ = ABCMeta

          def __init__(self, serial, agent):
            self.serial = serial
            self.agent = agent

          '''
          Callback that is executed for any operation received
          '''
          @abstractmethod
          def handleOperation(self, message): pass

          '''
          Returns a list of supported operations
          '''
          @abstractmethod
          def getSupportedOperations(self): pass

          '''
          Returns a list of supported SmartREST templates (X-Ids)
          '''
          @abstractmethod
          def getSupportedTemplates(self): pass
      
    Listeners are called whenever there is a message received on a subscribed topic.

3. Initializers

        class Initializer:
          __metaclass__ = ABCMeta

          def __init__(self, serial):
            self.serial = serial

          '''
          Returns a list of SmartREST messages. Will be called at the start of the agent
          '''
          @abstractmethod
          def getMessages(self): pass

    Initializers are only called once at the start of the agent.

You can take a look at the two example modules for how it can be used.

# Log
The logfile can be found in the .c8y-agent directory that you created

# Notes
I tested the agent so far only under Ubuntu 16.04 x64 with python 3.5.2
