'''
Created on 11/04/2014

@author: BurkeJ
'''
import json
import logging
from diff import Diff

log = logging.getLogger(__package__)

class Validate_Schema():

    def __init__(self, old_schema, new_schema):
        self.old_schema = old_schema
        self.new_schema = new_schema
        
        print json.dumps(self.old_schema, indent=4, sort_keys=True)
        print json.dumps(self.new_schema, indent=4, sort_keys=True)
        
    
    def compare(self):  
        test = self.old_schema == self.new_schema
        if test == True:
            return "Validation Passed"
        else:
            diff = Diff(self.old_schema, self.new_schema, True)
            return diff.difference
    
    def loop_dict(self, mydict):
        pass
    
    def loop_list(self, mylist):
        pass
    

if __name__ == '__main__':
    pass