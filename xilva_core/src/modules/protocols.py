#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np
import modules.utils as utils
"""
protocol classes.
Input: class it self
Output: solution functions includes:
    defaults,
    parts relationships,
    limits,
    positive directions(cf),
    other formats.
    The values are degrees
Return lists.
function <get_output> should provide the final output needed by the encoder.py
"""
class ibuki_gazebo():
    def __init__(self, _name = 'ibuki_gazebo'):
        print "protocol: using ibuki gazebo simulator."
        self._name = _name
        self.param_config = utils.read_yaml('xilva_core', self._name)
        self.directions = np.array(self.get_directions())
        self.defaults = np.array(self.get_defaults())
        self.maxlimit, self.minlimit = np.array(self.get_limits())
        self.mapping =np.array(self.get_mapping())
        self.groups = self.get_groups()
    def get_dof(self):
        print "get dofs"
        return self.param_config['dofs']
    def get_defaults(self):
        print "get defaults"
        return self.param_config['defaults']
    def get_directions(self):
        print "get directions"
        return self.param_config['directions']
    def get_limits(self):
        print "get limits"
        return self.param_config['limits']['max'], self.param_config['limits']['min']
    def get_mapping(self):
        print "get mapping"
        return self.param_config['mapping']
    "groups devides the dofs into functional groups, for diversity, and different functions"
    def get_groups(self):
        print "get groups"
        return self.param_config['groups']
        
    def get_output(self, payload_in):
        dic = {}
        for ele in self.groups.values():
            dic[ele] = 0
        output_buffer = np.take(payload_in, self.mapping)
        output_buffer = output_buffer * self.directions
        output_buffer = output_buffer + self.defaults
        np.clip(output_buffer, self.minlimit, self.maxlimit)
        "constraint limits"
        for (i,k) in enumerate(self.groups):
            dic[self.groups[k]] = (output_buffer[i])*0.0174
        return dic
            
        
class ibuki():
    def __init__(self, _name = 'ibuki'):
        print "protocol: using ibuki."
        self._name =  _name
        self.param_config = utils.read_yaml('xilva_core', self._name)
        self.directions = np.array(self.get_directions())
        self.defaults = np.array(self.get_defaults())
        self.maxlimit, self.minlimit = np.array(self.get_limits())
        self.mapping =np.array(self.get_mapping())
        self.groups = self.get_groups()
        
    def get_dof(self):
        return self.param_config['dofs']
    def get_defaults(self):
        return self.param_config['defaults']
    def get_directions(self):
        print "get directions"
        return self.param_config['directions']
    def get_limits(self):
        print "get limits"
        return self.param_config['limits']['max'], self.param_config['limits']['min']
    def get_mapping(self):
        print "get mapping"
        return self.param_config['mapping']
    "groups devides the dofs into functional groups, for diversity, and different functions"
    def get_groups(self):
        print "get groups"
        return self.param_config['groups']
    def get_output(self, payload_in):
        dic = {}
        "get mbed format string output with names - EvansStrings"
        output_buffer = np.take(payload_in, self.mapping)
        output_buffer = output_buffer * self.directions
        output_buffer = output_buffer*3.33 + self.defaults
        "constraint limits"
        output_buffer = np.clip(output_buffer, self.minlimit, self.maxlimit)
        for elements in self.groups:
            payload = np.take(output_buffer, self.groups[elements])
            embed_msg = utils.merge(payload)
            dic[elements] = embed_msg
        return dic
            
            
        
class commu_with_mobility():
    def __init__(self, _name = 'commu_with_mobility'):
        print "protocol: using commu with mobility."
        self._name =  _name
        self.param_config = utils.read_yaml('xilva_core', self._name)
    def get_dof(self):
        return self.param_config('dofs')
    def get_defaults(self):
        return self.param_config('defaults')
    def get_directions(self):
        print "get directions"
        return self.param_config['directions']
    def get_limits(self):
        print "get limits"
        return self.param_config['limits']['max'], self.param_config['limits']['min']
    def get_mapping(self):
        print "get mapping"
        return self.param_config['mapping']
    "groups devides the dofs into functional groups, for diversity, and different functions"
    def get_groups(self):
        print "get groups"
        return self.param_config['groups']
    def get_output(self, payload_in):
        "get mbed format string output with names - EvansStrings"
        cmbed = "yohee"
        return cmbed