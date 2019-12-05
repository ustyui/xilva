#!/usr/bin/env python2

import rospy
import modules.motions as motions
import modules.topics as topics

angles = {0:10, 1:-10, 13:10}

#if __name__ == "__main__":
#    nh = rospy.init_node("setangles")
#    s = motions.Joints(topics.slave[0])
#    
#    rospy.loginfo("DEMO STARTED")
#
#    s.reset()
#    while not rospy.is_shutdown():
#        
#        s.set_angles_to(angles, 2)
#        rospy.sleep(1)
#    
#    rospy.loginfo("DEMO FINISHED")
    
#if __name__ == "__main__":
#    nh = rospy.init_node("setangles")
#    s = motions.JointInterrupt()
#    
#    rospy.loginfo("DEMO STARTED")
#
#    s.interrupt_reset()
#    while not rospy.is_shutdown():
#        
#        s.set_angles_to_channel(angles, 2)
#        rospy.sleep(1)
#        
#    s.interrupt_reset()
#    rospy.loginfo("DEMO FINISHED")

#if __name__ == "__main__":
#    nh = rospy.init_node("setangles")
#    s = motions.Behaviors(0)
#    
#    rospy.loginfo("DEMO STARTED")
#
#    while not rospy.is_shutdown():
#        
#        s.doitnow(angles)
#        rospy.sleep(1)
#        
#    s.compeleted()
#    rospy.loginfo("DEMO FINISHED")

if __name__ == "__main__":
    nh = rospy.init_node("setangles")
    s = motions.Behaviors(topics.slave[1])
    
    rospy.loginfo("DEMO BEHAVIOR DOITLATER STARTED")

    while not rospy.is_shutdown():
        
        s.doitlater(angles)
        rospy.sleep(1)
        s.compeleted()
        rospy.sleep(1)
    
    rospy.loginfo("DEMO FINISHED")