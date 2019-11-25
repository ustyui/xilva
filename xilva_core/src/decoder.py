#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import rospy
from xilva_core.msg import Evans

import modules.utils as utils
import modules.topics as topics
import modules.protocols as xprotocols
import modules.logging as logs

import sys

"""
The decoder translates sensor messages of a robot into Evans format.
During this procedure, we change the protocol, and The sensor messages 
are put into a xilva order.
This procedure is called generalization.
"""

"receive the type of robot from the argv"
dev_name = sys.argv[1]

class Received_msg(object):
    def __init__(self):
        self._name = 'noname'
        self._level = 1
        self._msgid = 1
        self._payload = []
        
def callback(msg, args):
    instance = args
    instance._name = msg.name
    instance._level = msg.level
    instance._msgid = msg.msgid
    instance._payload = msg.payload

"4. publish the output using the protocol"
if __name__ == "__main__":
    
    param_config = utils.read_yaml('xilva_core', 'config')
    _RATE = param_config['rate']
    
    nh = rospy.init_node('X_encoder', anonymous=True)
    rate = rospy.Rate(_RATE)
    
    message = Received_msg()
    "activate logging"
    logtext = logs.Roslog('X_encoder')
    
    "receive the mixer message from the bus"
    sub = rospy.Subscriber(topics.comm['bus'], Evans, callback, message)
    "decide the protocol to use"
    if (dev_name == "ibuki_gazebo"):
        protocol = xprotocols.ibuki_gazebo()
    elif (dev_name == "ibuki"):
        protocol = xprotocols.ibuki()
    elif (dev_name == "commu_with_mobility"):
        protocol = xprotocols.commu_with_mobility()
    else:
        rospy.logfatal(logtext.report_log(11))
    