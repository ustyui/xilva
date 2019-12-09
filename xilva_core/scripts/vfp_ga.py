#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 10:55:57 2019
In this example a simple motion is evolved in gazebo physics environment engine.
After running this program for some time, you can start having a look at some envolved
motion by opening up some of the generated csv using silva HSM_csv.py function in the gazebo simulator.
@author: ibukidev
"""

import rospy
from xilva_core.msg import Evans
from contact_republisher.msg import contact_msg
from contact_republisher.msg import contacts_msg

import modules.utils as utils
import modules.topics as topics

from subprocess import Popen
import time
import json

import numpy as np
import random

OKGREEN = '\033[92m'
ENDC = '\033[0m'

AGENT_NUM = 16
GENERATION_NUM = 1000
WAIT_TIME = 10
RATE = 50

_ku = 0.2

robot_name = 'ibuki'
_DRIVEUNITS = rospy.get_param(robot_name+'/drive_units')

        
def crossover(parent1, parent2):
    child = np.zeros(15)
    startpoint = random.choice(list(enumerate(parent1)))[0]
    for idx in range(0, 7):
        cutter1 = idx + startpoint
        if cutter1 >= 15:
            # if cutter is ovr flow then minus 15 to buld a cycle
            cutter1 = cutter1 - 15
        # 7 chromosome from parent1
        child[cutter1] = parent1[cutter1]
    for idx in range(0, 8):
        # 8 chromosome from parent2
        cutter2 = idx + startpoint + 7
        if cutter2 >= 15:
            cutter2 = cutter2 - 15
        child[cutter2] = parent2[cutter2]
        
    return child

def mutate(people):
    # here firstly only negitave is used in the mutation
    mutatepoint = random.choice(list(enumerate(people)))[0]
    people[mutatepoint] = -people[mutatepoint]
        
    return people
        

class Motion():
    def __init__(self):
        self.pub_msg = Evans()
        self.pub = rospy.Publisher(topics.reflex[0], Evans, queue_size=10)
        self._payload = [0.0]*_DRIVEUNITS
        # 15 dofs
        self._act_dofs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        
        self.collision_count = 0
        
    def simple_motion(self, timecnt):
        for idx in self._act_dofs:
            self._payload[idx] = timecnt
        utils.make_message(self.pub_msg, 'evo', 0, 0, self._payload)
        
    def joints_motion(self, position):
        for idx in self._act_dofs:
            self._payload[idx] = position[idx]
        utils.make_message(self.pub_msg, 'ga', 0, 0, self._payload)
        
    def motion_playback_simple(self,):
        for _counter in range(0,10):
            self.simple_motion(_counter*10)
            time.sleep(0.2)
            self.pub.publish(self.pub_msg)
        for _counter in range(10,20):
            self.simple_motion(190-_counter*10)
            time.sleep(0.2)
            self.pub.publish(self.pub_msg)
            
    def motion_playback(self, v_position):
        # v_position: the maximum of the motion, put it into motion gauge
        # v_position indices should be 0~ 15
        # v_timing: the timing of moving the joint
        # v_velocity: the speed of joint motion
        np_position = np.array(v_position)
        np_pos_step = np_position/10.0
        # devide the moiton into n pieces, publish them in this rate
        for _counter in range(0,10):
            self.joints_motion(np_pos_step*_counter)
            time.sleep(0.2)
            self.pub.publish(self.pub_msg)
            
        for _counter in range(0,11):
            self.joints_motion(np_position-np_pos_step*_counter)
            time.sleep(0.2)
            self.pub.publish(self.pub_msg)
            
def collision_counter_cb(msg, args):
    instance = args
    
    collision_data = msg.contacts[0].collision_2
    
    if collision_data !='ground_plane::link::collision':
        instance.collision_count += 1

if __name__ == "__main__":
    # init ros node
        
    # event variables related with the agnets
    gazebo_motion = [0]*AGENT_NUM
    unfitness = [0]*AGENT_NUM
    
    # the motion initialization
    for idx in range (0, AGENT_NUM):
        
        gazebo_motion[idx] = 140*np.random.normal(size=15)
    
    for gen in range(0, GENERATION_NUM):
        
        print "\n\n"
        print "----------------------------------"
        print "---------- GENERATION", gen, "----------"
        print "----------------------------------"
        print "\n"
        
        # decide the agent configuration for each generation
        # logging
        
        for idx in range(0, AGENT_NUM):
            # initialize the variables and parameters
            nh = rospy.init_node("GA_exp_postures")
            input_motion = Motion()
            sub = rospy.Subscriber('/forces', contacts_msg, collision_counter_cb, input_motion)
            input_motion.collision_count = 0
            
            load_sys = Popen(['roslaunch', 'silva_core', 'core_ibuki.launch'])
            
            load_tester = Popen(['rosrun', 'ibuki_gazebo', 'tester.py'])
            time.sleep(1)
            
            load_world = Popen(['roslaunch', 'ibuki_gazebo', 'ibuki_evo.launch'])
            # load the parameter server
            load_param = Popen(['roslaunch', 'ibuki_gazebo', 'ibuki_param.launch'])
            time.sleep(1)
            print(OKGREEN+"Loaded Parameter Server"+ENDC)
            # spawn ibuki controller
            time.sleep(1)
            load_ctrl = Popen(['roslaunch', 'ibuki_control', 'ibuki_control.launch'])
            print(OKGREEN+"Spawned ibuki controller"+ENDC)
            # spawn an ibuki model
            load_ibuki = Popen(['rosrun', 'gazebo_ros', 'spawn_model', '-file', '/home/ibukidev/catkin_ws/src/silva/ibuki_description/urdf/ibuki.urdf', '-urdf', '-model', 'ibuki',\
                                '-z', '0.05'])
            # run the contact detector
            load_contact = Popen(['rosrun', 'contact_republisher', 'contact_republisher_node'])        
            # check if the environment is okay
            time.sleep(WAIT_TIME)
            # input some motion using rospy
            print (OKGREEN+"Carry out Motion "+str(gazebo_motion[idx])+ENDC)
            input_motion.motion_playback(gazebo_motion[idx])
            # detect confliction with gazebo object
            time.sleep(5)       
            
            # evaluate fitness
            moved_ranges = sum(abs(gazebo_motion[idx]))
            print (OKGREEN+"Collisoion count " +str(input_motion.collision_count)+ENDC)
            unfitness[idx] = input_motion.collision_count - _ku * moved_ranges
            # get the survive result
            print (OKGREEN+"UnFitness: " +str(unfitness[idx])+ENDC)
            time.sleep(1)
            
            # stop the contact detector
            load_contact.terminate()
            # delete the model
            kill_ibuki = Popen(["rosservice", "call", "gazebo/delete_model", "ibuki"])
            time.sleep(1)
            # delete the controller
            load_ctrl.terminate()
            # kill the parameter server
            load_param.terminate()

            load_world.terminate()
            
            load_tester.terminate()
            
            load_sys.terminate()
            
            time.sleep(17)
            
            #print(OKGREEN+"loop number "+str(idx)+ENDC)
            

            
            input_motion.collision_count = 0
            
            # move to the next generation
        
        # get the statics of the last generation and output files
        f = open('Gen'+str(gen)+'.txt', 'w')
        f.write(str(gen)+'\t\n')
        f.write(str(gazebo_motion)+'\t\n')
        f.write(str(unfitness)+'\t\n')
        f.close()
        
        # mating_pool: ring selection pairs to crossover
        # get childs of half the population
        half_num = int(AGENT_NUM/2)
        child = [0]*half_num
        # check: Agent_num = 4 that half_num = 2
        print gazebo_motion[1]
        for idx in range(0, half_num):
            parent1 = gazebo_motion[idx*2]
            parent2 = gazebo_motion[idx*2+1]
            
            child[idx] = crossover(parent1, parent2)
            # 2 childs
            
        print child
        
        # randomly choose some of the agents to mutate
        if gen>0:
            mutate_agent_id = random.randint(0, half_num-1)
            child[mutate_agent_id] = mutate(child[mutate_agent_id])
            
        print child
        
        # Parents selection: select via unfitness
        # get the ids of the selected parents
        unfitness = np.array(unfitness)
        select_parents_id = np.argpartition(unfitness, half_num)
        
        select_parents_id = select_parents_id[:half_num]
        # two ids
        
        # merge with half of the population, to to the next generation
        for idx in range(0, len(gazebo_motion)):
            if idx < half_num:
                gazebo_motion[idx] = gazebo_motion[select_parents_id[idx]]
            else:
                gazebo_motion[idx] = child[idx - half_num]
                
        # move to the next generation!

