from __future__ import print_function
import six

import os.path as osp
import json
from bz2 import BZ2File

'''
JASMIN stands for Json Assembly of Study Meta-Information for Neuroimaging.
It is a file format that can hold all information needed to create an
exposition service for neuroimaging data files.
'''

class JasminFile(object):
    '''
    Reads a JASMIN file and provides some methods to parse its contents.
    A JASMIN file is a bz2 compressed JSON file. The JSON contains a
    dictionary with the following structure:
    
    {framework}:
        'paths':
            {path}:
                'action_id':
                'generated_by_action':
                'generated_by_attribute':
                'size':
                'modality':
                'subject_uuid':
                'center_uuid':
                'time_point':
        'actions':
            {action_name}:
                {action_id}:
                    'types':
                        {name}: {type}
                    'inputs':
                        {name}: {value}
                    'outputs':
                        {name}: {value}
                    'attributes':
                        {name}: {value}
    '''
    def __init__(self, path):
        '''
        Read a JASMIN file.
        '''
        self.source_path = osp.normpath(osp.abspath(path))
        self.dict = json.load(BZ2File(self.source_path))
    
    
    def save(path=None):
        '''
        Save JASMIN file.
        '''
        if path is None:
            path = self.source_path
        json.dump(self.dict, BZ2File(path,'w'))
    
    
    @property
    def framework(self):
        '''
        Returns the name of the framework if there is only one in the Jasmin 
        file. Otherwise raises a KeyError with an explicit error message.
        '''
        frameworks = self.dict.keys()
        if len(frameworks) == 1:
            return frameworks[0]
        else:
            raise KeyError('Jasmin file {0} contains several frameworks '
                           '({1}). One must be choosen explictely'.format(
                               self.source_path, ','.join(frameworks)))
    
    def iter_paths(self, framework=None):
        '''
        Iterate over all paths in a given framework (by default uses
        self.framework). Yields (path, path_dict) attributes where
        path is a path (relative to the directory containing the JASMIN
        file) and path_dict are the attributes of the path.
        '''
        if framework is None:
            framework = self.framework
        return six.iteritems(self.dict[framework]['paths'])
    
    
    def path(self, path, framework=None):
        '''
        Returns the attributes of a given path in a given framework (by
        default uses self.framework).
        '''
        if framework is None:
            framework = self.framework
        return self.dict[framework]['paths'][path]
    
    
    def iter_actions(self, action_names=None, framework=None):
        '''
        Iterate over actions in a given framework (by default uses
        self.framework). It is possible to restrict the result to
        action with a given action_name. Yields one dictionary for
        each action.
        '''
        if framework is None:
            framework = self.framework
        if action_names is None:
            action_names = self.dict[framework]['actions'].keys()
        for action_name in action_names:
            for action_id, action_dict in six.iteritems(self.dict[framework]['actions'][action_name]):
                action = action_dict.copy()
                action['action_name'] = action_name
                action['action_id'] = action_id
                yield action
    
    
    def action(self, action_id, framework=None):
        '''
        Return an action dictionary for the given action_id in a given
        framework (by default uses self.framework). 
        '''
        if framework is None:
            framework = self.framework
        actions = self.dict[framework]['actions']
        for action_name in actions.keys():
            action_dict = actions[action_name].get(action_id)
            if action_dict is not None:
                action = action_dict.copy()
                action['action_name'] = action_name
                action['action_id'] = action_id
                return action
        raise KeyError('No action with action_id={0}'.format(repr(action_id)))
    