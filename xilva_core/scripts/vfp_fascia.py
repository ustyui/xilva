#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 10:00:41 2019

@author: ibukidev
"""
import rospy
import numpy as np

import modules.utils as utils
import modules.topics as topics

from xilva_core.msg import Evans

RIGHT = 1
LEFT = -1

#deg = np.array([0, 0, 30, 0, 30, 30])
#w0, w1, w2, w3, w4, w5= 0, 0, 1, 0, 1, 1
#line = np.array([w0, w1, w2, w3, w4, w5])
#topology = {'a':[2,4], 'b':[2,5]}
#direction = np.array([0, 0, -1, 0, -1, 1])
#length = sum(line*deg*direction)
fascia_name = ['sbl', 'sfll', 'sflr', 'lll', 'llr', 'spll', 'splr', 'dfall', 'dfalr', 'sfall', 'sfalr', 'dball', 'dbalr', 'sball', 'sbalr']

class Network():
    def __init__(self):
        self.param_config = utils.read_yaml('xilva_core', 'ibuki_gazebo')
        "relationships"
        self.mapping = self.param_config['mapping']

        self.angles = np.array([])
        "the selected angles are joints that are used in all fascia system"
        self.selected_angles = np.array([])
        "the line angles are joint angles that are used in a specific line"
        self.myu = 0.1
        self.pub_msg = Evans()
        
        
        self.sub = rospy.Subscriber('/silva/slave_local/vfp', Evans, self.callback)
        self.pub = rospy.Publisher(topics.slave[2], Evans, queue_size=2)
    def callback(self, msg):
        self.angles = np.array(msg.payload)
#        print self.angles
#        print msg.payload
    
    def get_output(self, payload_in, fascia_name):
        "initialization"
        lengths = 0.0
        est_tension = 0.0
        
        fasciamap = np.array(self.param_config['fascia_select'][fascia_name])
        direction = np.array(self.param_config['fascia_direction'][fascia_name])
        "on the left of join=-1"
        force_dir = np.array(self.param_config['force_direction'][fascia_name])
        self.selected_angles = np.take(payload_in, self.mapping)
        line_angles = np.take(payload_in, fasciamap)
        weights = np.take(np.array([1]*len(payload_in)), fasciamap)
        
        lengths = utils.negative_to_zero(sum(weights*line_angles*direction))
        est_tension = lengths*self.myu
        "calculate estimated torque"
        line_rads = np.deg2rad(line_angles)
        line_sines = np.sin(line_rads)
        est_torque = -self.myu*est_tension*line_sines*force_dir
        "why direction: the tense force is applied always the same direction with fasica looses"
        line_outangles = np.rad2deg(line_rads + est_torque)
        "put it into normal output"
        output = payload_in.copy()
        np.put(output, fasciamap, line_outangles)
        
        print fascia_name, "estimate tension:", est_tension
        print fascia_name, "input rads:", line_rads
        print fascia_name, "input sines:", line_sines
        print fascia_name, "estimate torque:", est_torque
        print fascia_name, "input angles:", line_angles
        print fascia_name, "output angles:",line_outangles
        print fascia_name, "final output:", output
        
        return output
        
        
if (__name__ == "__main__"):
    nh = rospy.init_node("vfp_fascia")
    rate = rospy.Rate(20)
    vfp = Network()
    
    while not rospy.is_shutdown():
        if (vfp.angles != []):
            break
        rospy.sleep(0.5)
        rospy.loginfo("Waiting messages...")
        
    while not rospy.is_shutdown():
        
        vfp_buffer = vfp.angles
        print "first vfpbuffer:", vfp_buffer, vfp.angles
        output_sfll = vfp.get_output(vfp_buffer, 'sfll')
        print "second vfpbuffer:", vfp_buffer, vfp.angles
        output_sflr = vfp.get_output(vfp_buffer, 'sflr')
        
        print "sfll out:", output_sfll
        print "sflr_out:", output_sflr
        print "sum:", 0.5*output_sfll+ 0.5*output_sflr
        print "vfpangles:",vfp.angles
       
        utils.make_message(vfp.pub_msg, 'vfp', 0, 0, output_sfll)
        
        vfp.pub.publish(vfp.pub_msg)
        
        rate.sleep()