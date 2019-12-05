#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 22:36:12 2019
FK #1
@author: ustyui
"""
import rospy
import utils, topics
from xilva_core.msg import Evans

class JointInterrupt(object):
    """
    designate a robot as a combination of Joints
    """
    
    def __init__(self):
        self.joints = None
        self.angles = None
        self.pub = [[],[],[],[]]
        self.pub_msg = Evans()
                        
        self.robot_name = rospy.get_param('/xilva/ref_robot')
        driveunits = rospy.get_param(self.robot_name+'/drive_units')
        
        # read joint dict and initialize
        self.joints = {}
        self.zeros = {}
        for idx in range(0, driveunits):
            self.joints[idx] = 0
            self.zeros[idx] = 0
             
        rospy.loginfo("Joints populated")
        
        # create publisher
        self.pub[0] = rospy.Publisher(topics.interrupts[0], Evans, queue_size=3)
        self.pub[1] = rospy.Publisher(topics.interrupts[1], Evans, queue_size=3)
        self.pub[2] = rospy.Publisher(topics.interrupts[2], Evans, queue_size=3)
        self.pub[3] = rospy.Publisher(topics.interrupts[3], Evans, queue_size=3)

    def set_angles(self, angles):
        self.angles = self.joints
        for j,v in angles.items():
            if j not in self.joints:
                rospy.logerror("Invalid joint number" +j)
                continue
            # encode joints
            self.angles[j] = v
            
        return self.angles
    def set_angles_to_channel(self, angles, this_topic):
        encoded_angles = self.set_angles(angles).values()
        # change dict to list
        print encoded_angles
        utils.make_message(self.pub_msg,'int',0,0,encoded_angles)
        rospy.set_param(self.robot_name+'/sys_interrupt', 1)
        self.pub[this_topic].publish(self.pub_msg)
        
        
    def interrupt_reset(self):
        utils.make_message(self.pub_msg,'int',0,0,self.zeros.values())
        rospy.set_param(self.robot_name+'/sys_interrupt', 0)
        for idx in range(0,3):
            self.pub[idx].publish(self.pub_msg)
        
class Joints(JointInterrupt):
    def __init__(self, channel):
        JointInterrupt.__init__(self)
        self.pub = rospy.Publisher(channel, Evans, queue_size=3)
    def set_angles(self, angles):
        self.angles = self.joints
        for j,v in angles.items():
            if j not in self.joints:
                rospy.logerror("Invalid joint number" +j)
                continue
            # encode joints
            self.angles[j] = v
        return self.angles
            
    def set_angles_to(self, angles, this_topic=None):
        print angles
        encoded_angles = self.set_angles(angles).values()
        # change dict to list
        print encoded_angles
        utils.make_message(self.pub_msg,'motion',0,0,encoded_angles)
        self.pub.publish(self.pub_msg)    

    def reset(self):
        utils.make_message(self.pub_msg,'motion',0,0,self.zeros.values())
        
        self.pub.publish(self.pub_msg)    
        
class Behaviors(JointInterrupt):
    def __init__(self, channel):
        JointInterrupt.__init__(self)

        self.channel = 0
        if (type(channel)==int):
            self.channel = channel
        else:
            self.pubjoint = rospy.Publisher(channel, Evans, queue_size=3)                
    def set_angles_to(self, angles, this_topic=None):
        encoded_angles = self.set_angles(angles).values()
        # change dict to list
        print encoded_angles
        utils.make_message(self.pub_msg,'behavior',0,0,encoded_angles)
        self.pubjoint.publish(self.pub_msg)      
    def reset(self):
        utils.make_message(self.pub_msg,'behavior',0,0,self.zeros.values())
        self.pubjoint.publish(self.pub_msg)    
    
    def doitnow(self, angles):
        self.set_angles_to_channel(angles, self.channel)
        return None
    def doitlater(self, angles):
        self.set_angles_to(angles)
        return None
    def compeleted(self):
        try: 
            self.interrupt_reset()
        except AttributeError:
            self.reset()
        self.reset()