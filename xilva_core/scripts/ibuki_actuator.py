#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from xilva_core.msg import EvansString

import socket, errno, sys, os

import modules.utils as utils
import modules.logging as logs


_RATE = 40

class Joint():
    def __init__(self):
        self.payloads = {'neck': '',
                         'arml': '',
                         'armr': '',
                         'handl': '',
                         'handr': '',
                         'headl': '',
                         'headc': '',
                         'headr': '',
                         'hip': '',
                         'wheel':''}

def callback(msg, args):
    instance = args
    instance.payloads[msg.name] = msg.payload
"socket initialization"
"a subscriber to receive and send"
"get ip, port"
if __name__ == "__main__":
    
    motorsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    nh = rospy.init_node('ibuki_actuators', anonymous = True)
    param_config = utils.read_yaml('xilva_core', 'ibuki')
    
    _IP = param_config['IP']
    _PORT = param_config['PORT']            
    rate = rospy.Rate(_RATE)
    
    mbed_joint = Joint()   
    logtext = logs.Roslog("ibuki_actuator")
    sub = rospy.Subscriber('/ibuki/encoded_commands', EvansString, callback, mbed_joint)
    
    while not rospy.is_shutdown():
        for elements in mbed_joint.payloads:
            embed_msg = mbed_joint.payloads[elements]
            try:
                motorsock.sendto(embed_msg, (_IP[elements], _PORT[elements]))
            except socket.error as error:
                if error.errno == errno.ENETUNREACH:
                    rospy.logfatal_once(logtext.report_log(99))
                else:
                    raise
        rate.sleep()
            
                