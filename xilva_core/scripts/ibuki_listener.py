#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from xilva_core.msg import EvansString

import socket, errno, sys, os

import modules.utils as utils
import modules.logging as logs

network_flag = 0 

if __name__ == "__main__":
    
    nh = rospy.init_node('ibuki_netlistener', anonymous = True)
    logtext = logs.Roslog('ibuki_netlistener')
    param_config = utils.read_yaml('xilva_core', 'ibuki')
    
    _IP = param_config['IP']
    _PORT = param_config['PORT']       
    parts_name = ['neck', 'arml', 'armr', 'handl', 'handr', 'headl', 'headc', 'headr', 'hip', 'wheel']     
    
    rate =rospy.Rate(1)
    while not rospy.is_shutdown():
        for dev_name in parts_name:
            response = os.system("ping -c 1 " +_IP[dev_name]+" -w 1 >/dev/null 2>&1")
            if response != 0:
                "interrupt 0 in the future"
                network_flag = 99
                rospy.logwarn('network erros')
#                rospy.logwarn(logtext(2))
            else:
                if network_flag == 99:
                    network_flag = 0
                    rospy.loginfo(dev_name+": Network re-established.")
                else:
                    pass
            
        rate.sleep()