import os
import sys
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
from mqtt_init import *

# Creating Client name - should be unique 
global clientname
r = random.randrange(1, 10000000)
clientname = "IOT_client-Id-" + str(r)
dust_topic = 'CleanRobotComputer/Dust'
temperature_topic = 'CleanRobotComputer/Temperature'
time_topic = 'CleanRobotComputer/Time'
publish_topic = 'SmartCleanRobotManagerApp'
global ON
ON = False

class Mqtt_client():
    
    def __init__(self):
        # broker IP address:
        self.broker = ''
        self.port = 0
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.on_connected_to_form = ''
        self.temperature = 0
        self.dust = 0
        self.time = ''
        
    # Setters and getters
    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    def get_broker(self):
        return self.broker
    def set_broker(self, value):
        self.broker = value
    def get_port(self):
        return self.port
    def set_port(self, value):
        self.port = value
    def get_clientName(self):
        return self.clientname
    def set_clientName(self, value):
        self.clientname = value
    def get_username(self):
        return self.username
    def set_username(self, value):
        self.username = value
    def get_password(self):
        return self.password
    def set_password(self, value):
        self.password = value
        
    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)
            
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        print("Disconnected result code " + str(rc))
            
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print(f"message from {topic}: {m_decode}")
        
        if topic == dust_topic:
            self.dust = float(m_decode)
        elif topic == temperature_topic:
            self.temperature = float(m_decode)
        elif topic == time_topic:
            self.time = m_decode

        self.check_conditions()

    def check_conditions(self):
        if self.temperature > 28 or self.dust > 22 or self.time == "03":
            self.publish_to(publish_topic, "It's time to clean the house")

    def connect_to(self):
        # Init paho mqtt client class
        self.client = mqtt.Client(self.clientname, clean_session=True) # create new client instance
        self.client.on_connect = self.on_connect  # bind call back function
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)  # connect to broker
    
    def disconnect_from(self):
        self.client.disconnect()
    
    def start_listening(self):
        self.client.loop_start()
    
    def stop_listening(self):
        self.client.loop_stop()
    
    def subscribe_to(self, topic):
        self.client.subscribe(topic)
              
    def publish_to(self, topic, message):
        self.client.publish(topic, message)
        
class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self, mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID = QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName = QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL = QCheckBox()
        
        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)
        
        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")
        
        self.eSubscribeTopic = QLineEdit()
        self.eSubscribeTopic.setText(f"{dust_topic}, {temperature_topic}, {time_topic}")

        self.ePushtbtn = QPushButton("", self)
        self.ePushtbtn.setToolTip("Push me")
        self.ePushtbtn.setStyleSheet("background-color: gray")

        formLayout = QFormLayout()
        formLayout.addRow("Turn On/Off", self.eConnectbtn)
        formLayout.addRow("Sub topics", self.eSubscribeTopic)
        formLayout.addRow("Status", self.ePushtbtn)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Connect")
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
                    
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())        
        self.mc.connect_to()        
        self.mc.start_listening()
        for topic in self.eSubscribeTopic.text().split(', '):
            self.mc.subscribe_to(topic)
    
    def update_btn_state(self, text):
        global ON
        if ON:
            self.ePushtbtn.setStyleSheet("background-color: gray")
            ON = False
        else:
            self.ePushtbtn.setStyleSheet("background-color: red")
            ON = True
        
class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc = Mqtt_client()
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 300, 300, 150)
        self.setWindowTitle('SmartCleanRobotManagerApp')  
              
        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)        
        
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
