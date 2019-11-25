#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 15:06:54 2019
topic management
@author: ustyui
"""

comm = \
{'bus':   '/silva/joint_local/mixer',
 'default': '/silva/joint_local/default',
 'states':  '/silva/states',
 'joy':     '/joy',
 'idle':    '/silva/joint_local/idle',
 'reflex':  '/silva/joint_local/reflex',
 'slave':   '/silva/joint_local/slave',
 'auto' :   '/silva/joint_local/auto'
        }

feedback = \
{'wheelencoder':    '/silva/reflex_local/feedback'
 }

slave = \
['/silva/slave_local/intention', # use whole-body mapping
 '/silva/slave_local/walking', # use whole-body mapping
 '/silva/slave_local/operation', # use whole-body mapping
 '/silva/slave_local/decision',
 '/silva/slave_local/hsm'

]

idle = \
['/silva/idle_local/ch0',
 '/silva/idle_local/intention'

]

reflex = \
['/silva/reflex_local/ch0',
 '/silva/reflex_local/ch1',
 '/silva/reflex_local/ch2',
 '/silva/reflex_local/feedback'
]

auto = \
['/silva/auto_local/ch0',
 '/silva/auto_local/ch1',
 '/silva/auto_local/ch2',
 '/silva/auto_local/ch3'
]

interrupts = \
['/silva/interrupts/ch0',
 '/silva/interrupts/ch1',
 '/silva/interrupts/ch2',
 '/silva/interrupts/ch3'
 ]

norm_ch = [slave, idle, reflex, auto]
norm_channel_lengths = len(slave) + len(idle) + len(reflex) + len(auto)
int_channel_lengths = len(interrupts)

# comment: maybe it is okay to add a temp topics here, for specific uses;


        

