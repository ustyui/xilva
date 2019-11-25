#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time
import sys
import modules.utils as utils

def time_stamp():
    # return time.strftime("[%Y/%m/%d-%H:%M:%S]")
    return ""

class Roslog(object):
    def __init__(self, _nodename):
        self._name = _nodename
    
    def report_log(self, _code):
        log_content = utils.read_yaml('xilva_core','logtexts')[_code]
        log_text = "code"+ str(_code) + ',' + self._name + ":" + log_content
        return log_text


class Printlog(object):
    def __init__(self):
        self.timers = {"start": time.time(), "last_call": time.time()}
        
    def add_timer(self, name):
        assert name not in self.timers
        self.timers[name] = time.time()
        
    def reset_timer(self, name):
        assert name in self.timers
        if name != "start":
            self.timers[name] = time.time()
            
    def seconds_from(self, timer_name):
        return time.time() - self.timers[timer_name]
    
    def message(self, content, timer_name = None, reset = True):
        if timer_name is None:
            print(time_stamp() + ' ' + content)
        else:
            s = self.seconds_from(timer_name)
            m, h = s/60.0, s / 3600.0
            print(time_stamp() + ' '  + content + ' \t (time from ' + timer_name + ': %0.2fs %0.2fm %0.2fh)' % (s, m, h))
            if reset:
                self.reset_timer(timer_name)
        
        sys.stdout.flush()
        sys.stderr.flush()