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
        "<parameters>"
        self.myu = 0.05
        self.pub_msg = Evans()
        
        self.sub = rospy.Subscriber('/silva/slave_local/vfp', Evans, self.callback)
#        self.sub = rospy.Subscriber('/silva/slave_local/vfp', Evans, self.callback)
        self.pub = rospy.Publisher(topics.slave[2], Evans, queue_size=2)
    def callback(self, msg):
        self.angles = np.array(msg.payload)
#        print self.angles
#        print msg.payload
    
    def get_est_deg(self, payload_in, fascia_name):
        "initialization"
        lengths = 0.0
        est_tension = 0.0
        
        fasciamap = np.array(self.param_config['fascia_select'][fascia_name])
        direction = np.array(self.param_config['fascia_direction'][fascia_name])
        "on the left of join=-1"
        force_dir = np.array(self.param_config['force_direction'][fascia_name])
        self.selected_angles = np.take(payload_in, self.mapping)
        line_angles = np.take(payload_in, fasciamap)
        "<parameters>"
        weights = np.take(np.array([1]*len(payload_in)), fasciamap)
        "direction:if the direction of fascia line extends same with current cf"
        lengths = utils.negative_to_zero(sum(weights*line_angles*direction))
        est_tension = lengths*self.myu
        "calculate estimated torque"
        line_rads = np.deg2rad(line_angles)
        line_sines = np.sin(line_rads)
        est_torque = self.myu*est_tension*np.abs(line_sines)*force_dir
        "force direction: the direction of fascia tense, if it is same with current cf"
        line_outangles = np.rad2deg(est_torque)
        "put it into normal output"
        output = np.array([0.0]*len(payload_in))
        np.put(output, fasciamap, line_outangles)
        
        print fascia_name, "estimate tension:", est_tension
#        print fascia_name, "input rads:", line_rads
#        print fascia_name, "input sines:", line_sines
#        print fascia_name, "estimate torque:", est_torque
#        print fascia_name, "input angles:", line_angles
#        print fascia_name, "output angles:",line_outangles
#        print fascia_name, "final output:", output
        
        return output
        
        
if (__name__ == "__main__"):
    nh = rospy.init_node("vfp_fascia")
    rate = rospy.Rate(20)
    vfp = Network()
    "<parameters>"
    w = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    while not rospy.is_shutdown():
        if (vfp.angles != []):
            break
        rospy.sleep(0.5)
        rospy.loginfo("Waiting messages...")
        
    while not rospy.is_shutdown():
        
        vfp_buffer = vfp.angles
#        print "first vfpbuffer:", vfp_buffer, vfp.angles
        output_sfll = vfp.get_est_deg(vfp_buffer, 'sfll')
#        print "second vfpbuffer:", vfp_buffer, vfp.angles
        output_sflr = vfp.get_est_deg(vfp_buffer, 'sflr')
        
        output_sbl = vfp.get_est_deg(vfp_buffer, 'sbl')
        
        output_lll = vfp.get_est_deg(vfp_buffer, 'lll')
        output_llr = vfp.get_est_deg(vfp_buffer, 'llr')
        "why spll[4] is 1: infact what effects in turning is Superior anterior iliac spine"
        output_spll = vfp.get_est_deg(vfp_buffer, 'spll')
        output_splr = vfp.get_est_deg(vfp_buffer, 'splr')
        "why dfal: based on ground truth of my own body"
        output_dfall = vfp.get_est_deg(vfp_buffer, 'dfall')
        output_dfalr = vfp.get_est_deg(vfp_buffer, 'dfalr')        
        
        output_sfall = vfp.get_est_deg(vfp_buffer, 'sfall')
        output_sfalr = vfp.get_est_deg(vfp_buffer, 'sfalr')
        "why dbal no [9]: because it is related with the wrist pitch, which ibuki don't have"
        output_dball = vfp.get_est_deg(vfp_buffer, 'dball')
        output_dbalr = vfp.get_est_deg(vfp_buffer, 'dbalr')
        
        output_sball = vfp.get_est_deg(vfp_buffer, 'sball')
        output_sbalr = vfp.get_est_deg(vfp_buffer, 'sbalr')
    
        "w: the weight of a specific fascia line input."
        result = w[0]*output_sfll + w[1]*output_sflr + w[2]*output_sbl + \
        w[3]*output_lll + w[4]*output_llr + w[5]*output_spll + w[6]*output_splr +\
        w[7]*output_dfall + w[8]*output_dfalr + w[9]*output_sfall + w[10]*output_sfalr +\
        w[11]*output_dball + w[12]*output_dbalr + w[13]*output_sball + w[14]*output_sbalr
        
        output_all = vfp.angles + result
        
        print "input:", vfp.angles
        print "sfll out:", output_sfll
        print "sflr_out:", output_sflr
        print "sum:", result
        print "output:",output_all
       
        utils.make_message(vfp.pub_msg, 'vfp', 0, 0, output_all)
        
        vfp.pub.publish(vfp.pub_msg)
        
        rate.sleep()