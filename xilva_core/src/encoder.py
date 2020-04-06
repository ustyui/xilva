#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import rospy
from xilva_core.msg import Evans

import modules.utils as utils
import modules.topics as topics
import modules.protocols as xprotocols
import modules.logging as logs

import sys
import numpy as np


"""
Encoder can catogrize the general Evans message into driver commands of the robots.
By choosing the format of the robot, the encoder completes
dof/unit mapping, protocol transformation by exploiting the human part of an android.
This procedure also can be called personalization.
"""
"receive the type of robot from the argv"
dev_name = sys.argv[1]
if dev_name == 'ibuki_gazebo':
    from ibuki_gazebo.ibuki import Ibuki
if dev_name == 'aoi_gazebo':
    from ibuki_gazebo.Aoi import Aoi
if dev_name == 'ibuki':
    from xilva_core.msg import EvansString
    pub_msg = EvansString()
    pub_ibuki = rospy.Publisher('/ibuki/encoded_commands', EvansString, queue_size=2)


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
    
    nh = rospy.init_node('X_encoder')
    rate = rospy.Rate(_RATE)
    
    message = Received_msg()
    "activate logging"
    logtext = logs.Roslog('X_encoder')
    
    "receive the mixer message from the bus"
    sub = rospy.Subscriber(topics.comm['bus'], Evans, callback, message)
    "decide the protocol to use"
    if (dev_name == "ibuki_gazebo"):
        protocol = xprotocols.ibuki_gazebo()
        robot = Ibuki()
    elif (dev_name == "aoi_gazebo"):
        protocol = xprotocols.ibuki_gazebo()
        robot = Aoi()
    elif (dev_name == "ibuki"):
        protocol = xprotocols.ibuki()
    elif (dev_name == "commu_with_mobility"):
        protocol = xprotocols.commu_with_mobility()
    else:
        rospy.logfatal(logtext.report_log(11))
    
    "output memory"
    while not rospy.is_shutdown():
        if (message._payload != []):
            break
        rospy.sleep(0.5)
        rospy.loginfo("Waiting messages...")
    while not rospy.is_shutdown():
        
        "since the output is obtained, choose where it goes"
        if (dev_name == "ibuki_gazebo"):
            output = protocol.get_output(message._payload)
            robot.set_angles(output)
        if (dev_name == "aoi_gazebo"):
            output = protocol.get_output(message._payload)
            robot.set_angles(output)        
        if (dev_name == 'ibuki'):
            output = protocol.get_output(message._payload)
            for elements in output:
                pub_msg.header.stamp = rospy.Time.now()
                pub_msg.name = elements
                pub_msg.payload = output[elements]
                pub_ibuki.publish(pub_msg)
            "make the payload"
            "make the message with dict name"
            "publish"
                    
        #TODO: commu
        rate.sleep()
        "make message"
