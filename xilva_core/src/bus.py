#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import rospy
from xilva_core.msg import Evans
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32MultiArray

import numpy as np
import threading

import modules.utils as utils
import modules.logging as logs
import modules.topics as topics

"The memory of joint_means is stored in class Mixer"
"Also the state msgs and the sensor msgs"
class Mixer(object):
    def __init__(self, dev_name):

        self._name = dev_name
        "check the system availibity"
        while not rospy.is_shutdown():
            if rospy.has_param(dev_name+'/drive_units'):
                break
            rospy.sleep(1)
            rospy.loginfo("Waiting for dynamic parameters to be updated...")
        rospy.loginfo("Parameters updated.")
        
        "initialize normal and interrupt channels"
        self._pub_msg = Evans()
        self._state_msg = Float32MultiArray()
        "mask high number and mask low number, to make a mask"
        "if the dofs is odd, mln is 1 bigger than mhn"
        self._mhn = _DRIVEUNITS/2
        self._mask_h = np.zeros(self._mhn)
        if _DRIVEUNITS%2 != 0:
            self._mask_l = np.zeros(_DRIVEUNITS/2 + 1)
            self._mln = self._mhn + 1
        else:
            self._mask_l = np.zeros(_DRIVEUNITS/2)
            self._mln = self._mhn
        self._mask = []
        
        "callbacked variables"
        self.wei_irsa = np.zeros(4)
        self._joy_data = np.zeros(8)
        self.joint_means = np.zeros(_DRIVEUNITS)
        "joint memory: are divided according to the framework of the system"
        """
        normal channel:[[channel1],[channel2],[channel3],...]
        channel1 = [[subchannel1],[subchannel2], ...]
        interrupt channel: [channel1],[channel2],...]
        """
        self.payload_norm = np.array([np.array([np.array([0] * rospy.get_param(dev_name+'/drive_units'))\
                                                for i in topics.norm_ch[j]]) for j in range(len(topics.norm_ch))])
        self.payload_int = [np.array([0] * rospy.get_param(dev_name+'/drive_units'))]\
                                              *topics.int_channel_lengths
        "weights of channels"
        self.weights_norm = np.array([np.array([[1] for i in topics.norm_ch[j]]) for j in range(len(topics.norm_ch))])
        self.weights_int = np.array([[1]]*topics.int_channel_lengths)
        
        "publishers"
        self.pub_p = rospy.Publisher(topics.comm['bus'], Evans, queue_size=5)
        self.pub_s = rospy.Publisher(topics.comm['states'], Float32MultiArray, queue_size=2)
        "subscribers"
        self.sub_joy = rospy.Subscriber(topics.comm['joy'], Joy, self.joy_cb)
        self.sub_normal =[[0 for i in topics.norm_ch[j]] for j in range(len(topics.norm_ch))]
        self.sub_interrupts = [[]]*topics.int_channel_lengths
        
        for (cid, subchannels) in enumerate(topics.norm_ch):
            for (subcid, channels) in enumerate(subchannels):
                self.sub_normal[cid][subcid] = rospy.Subscriber(channels, Evans, self.normal_cb, [cid, subcid])
        
        for i in range(0, len(self.sub_interrupts)):
            self.sub_interrupts[i] = rospy.Subscriber(topics.interrupts[i], Evans, self.interrupt_cb, i)
                   
    def joy_cb(self, msg):
        "main joystick controller kcontrol"
        if msg.header.frame_id == 'main':
            _axes = msg.axes
            "centerize"
            self._joy_data = np.array(_axes)+1.0
            "if the controller is dead raise slave channel"
            if sum(self._joy_data) == 0.0:
                self._joy_data[6] = 2.0

    def normal_cb(self, msg, args):
        ins1, ins2 = args[0], args[1]
        self.payload_norm[ins1][ins2] = np.array(msg.payload)
        
    def interrupt_cb(self, msg, args):
        instance = args
        self.payload_int[instance] = np.array(msg.payload)
        
    def borad_pub_d(self, rate, pub, msg, run_event):
        rate = rospy.Rate(rate)
        while run_event.is_set() and not rospy.is_shutdown():
            if isinstance(msg, Evans):
                msg.header.stamp = rospy.Time.now()
            "check if it is state msg"
            if isinstance(msg, Float32MultiArray):
                msg.data = self.wei_irsa
                
            pub.publish(msg)
            rate.sleep()
        
    def merge(self):
        if (rospy.get_param(self._name+'/weight_hw_adjust') == 1):
            self.wei_irsa = self._joy_data[4:]/2.0
        else:
            parameters = rospy.get_param(dev_name)
            self.wei_irsa = np.array([parameters['weight_idle'],
                            parameters['weight_reflex'],
                            parameters['weight_slave'],
                            parameters['weight_auto']])
    
        wei_irsa = self.wei_irsa
        "define the groups of joint irsa"
        joint_idle = sum(self.weights_norm[0]*self.payload_norm[0])
        joint_reflex = sum(self.weights_norm[1]*self.payload_norm[1])
        joint_slave = sum(self.weights_norm[2]*self.payload_norm[2])
        joint_auto = sum(self.weights_norm[3]*self.payload_norm[3])
        
        self.joint_means = np.array(wei_irsa[0]*joint_idle+ wei_irsa[1]*joint_reflex +\
                                wei_irsa[2]*joint_slave + wei_irsa[3]*joint_auto)
        "mask the joints"
        if (rospy.has_param(self._name+'/joint_mask_h') and rospy.has_param(self._name+'/joint_mask_l')):
            temp_mask = format(rospy.get_param(self._name+'/joint_mask_h'), '#0'+str(self._mhn+2)+'b')
            self._mask_h = np.array([int(m) for m in temp_mask[2:]])
            temp_mask = format(rospy.get_param(self._name+'/joint_mask_l'), '#0'+str(self._mln+2)+'b')
            self._mask_l = np.array([int(m) for m in temp_mask[2:]])
        else:
            rospy.logwarn_once("Mixer: Some dynamic parameters cannot be set for some reasons. This would lead to a constant output.")
        self._mask = np.concatenate((self._mask_h, self._mask_l), axis=0)
        
        self.joint_means = self._mask * self.joint_means
        
        return self.joint_means
    "if there is any interrupt message, do interrupt first"
    def sys_interrupt(self, confirm):
        if (confirm == 999):
            INT_joint_means = sum(self.weights_int*self.payload_int)
        return INT_joint_means
    
    "subscribers for normal channels, or interrupt channels"
    def start(self):
        loop_rate = rospy.Rate(_RATE)
        
        run_event = threading.Event()
        run_event.set()
        broad_state = threading.Thread(target = self.borad_pub_d, args = (_TRATE, self.pub_s, self._state_msg, run_event))
        broad_state.start()
        
        while not rospy.is_shutdown():
            Evans_payload = self.merge()
            "make message"
            utils.make_message(self._pub_msg, 'mixer', 1, 1, Evans_payload)
            self.pub_p.publish(self._pub_msg)
            loop_rate.sleep()

if __name__ == "__main__":
    
    nh = rospy.init_node("XBus")
    param_config = utils.read_yaml('xilva_core', 'config')
    "start xilva roslog"
    logtext = logs.Roslog("XBus")
    if (param_config == 0):
        rospy.logfatal(logtext.report_log(10))
    
    "Load Static Variables."
    dev_name = param_config['robot']
    _DRIVEUNITS = param_config['dofs']
    _RATE = param_config['rate']
    _TRATE = param_config['broadcast']
    
    "Set ROS parameters."
    rospy.set_param(dev_name, {'joint_mask_h': param_config['joint_mask_h'],
                               'joint_mask_l': param_config['joint_mask_l'],
                               'weight_hw_adjust': param_config['weight_hw_adjust'],
                               'weight_idle': param_config['weight_idle'],
                               'weight_reflex': param_config['weight_reflex'],
                               'weight_slave': param_config['weight_slave'],
                               'weight_auto': param_config['weight_auto'],
                               'sys_interrupt':0,
                               'drive_units': _DRIVEUNITS})
    
    rospy.loginfo("Xilva Xbus OK")
    
    Xbus = Mixer('ibuki')
    
    Xbus.start()
    
    
    
    
        
        
