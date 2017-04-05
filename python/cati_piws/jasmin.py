from __future__ import print_function
import six
import os
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
#    def __new__(cls,path):
##        if osp.isfile(path):
#            return super(JasminFile, cls).__new__(cls)
##        else:
##            return None

    def __init__(self,path,dic=None):
        '''
        Read a JASMIN file.
        '''
#        if(osp.isfile(path)):
#          self.path = osp.normpath(osp.abspath(path))
#          if dic is None :
#            self.dict = json.load(BZ2File(self.path))
#          else :
#            self.dict = dic
#        else :
#          self.path = path
#          if dic is not None :
#            self.dict = dic
#          else:
#            self.dict = None        
          
        self.path = osp.normpath(osp.abspath(path))
        if dic is None :
          self.dict = json.load(BZ2File(self.path))
        else :
          self.dict = dic


        #print("type : ", type(self.dict))
        #print(self.dict)
        #print(self.source_path)
        #print(json.dumps(self.dict, sort_keys=True,indent=4, separators=(',', ': ')))
        #print("framework found : ", json.dumps(self.dict['framework'], sort_keys=True,indent=4, separators=(',', ': ')))
        #print("framework, paths found : ", json.dumps(self.dict['framework']['paths'], sort_keys=True,indent=4, separators=(',', ': ')))
    
    
    def save(self, path=None):
        '''
        Save JASMIN file.
        '''
        if path is None:
            path = self.path
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
                           '({1}). One must be choosen explicitely'.format(
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
    
    
    def get_path(self, path, framework=None):
        '''
        Returns the attributes of a given path in a given framework (by
        default uses self.framework).
        '''
        if framework is None:
            framework = self.framework
#        print('Reading path : ', path)
#        print('framework : ', framework)
        if path in self.dict[framework]['paths'] :
          return self.dict[framework]['paths'][path]
        else :
          return None
    
    
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
    
    
    # Setters/Getters---------------------------
    # ------------------------------------------
    
    def set_framework(self, framework):
      self.framework = framework
    
    def set_path(self, path):
      self.path = osp.normpath(osp.abspath(path))
      
    def set_dict(self, dic):
      self.dict = dic
      
    @property
    def dictionary(self):
      return self.dict
    
    def get_attribute(self, attribute, dic, file_path, framework = None):
      '''
      Gets the value of a given attribute from a dictionary
      The dictionary is read from a .jasmin file
      '''
      if framework is None:
        framework = self.framework
      local_dic = self.get_path(file_path)
      if local_dic is not None :
        if attribute in local_dic :
          return local_dic[attribute]
        else :
          return None
      else :
        return False
        
    
class JasminIO(object):
  '''
  Provides an interface to access JASMIN files. This is necessary to find
  jasmin files without creating an occurence if it does not exist on disk.
  '''
  
  
  def read_attributes(self, file_path, path_attr = None):
    '''
    Reads a jasmin file and returns a dictionnary of attributes, if the 
    corresponding file path is defined in the jasmin file
    If path.jasmin exists : returns the dictionnary of attributes corresponding 
                            to the file given in argument
    Else : recursively goes up in file-tree, looking up for the first .jasmin 
           file found. When found, returns the dictionnary of attributes 
           corresponding to the file given in argument
    '''
    jasmin_path = file_path + '.jasmin'
    dic_res = None 
    if path_attr is None :
      path_attr = file_path
    
    if osp.isfile(jasmin_path) is True :
      j_object = JasminFile(jasmin_path)
      dic_res = j_object.get_path(path_attr)
      if dic_res is not None :
        return (dic_res, jasmin_path)
    
    else :
      if os.path.realpath(file_path) is '/' :
        return False
        
    dirpath, filename = os.path.split(jasmin_path)
    dirpath = str(os.path.abspath(os.path.join(dirpath, '..')) + '/')
    return self.read_attributes(dirpath, path_attr)
        
    
  def write_attributes(self, file_path, dic_to_write = None):
    '''
    Writes attribute on a jasmin file.
    If attribute exists : writes corresponding value on dictionary & save file
    Else : creates the attribute, write its value and save file
    '''
    jasmin_path = file_path + '.jasmin'
  
    if osp.isfile(jasmin_path) is False :
      j_object = JasminFile(jasmin_path, dic_to_write)
      j_object.save()
      return True
    else :     
      # TODO
      return False
      
      
  def get_attribute(self, attribute, path):
    '''
    Gets the value of a given attribute from a dictionary
    The dictionary is read from a .jasmin file
    '''
    dic = self.read_attributes(path)
    if dic is not False :
      j_object = JasminFile(dic[1])
      return j_object.get_attribute(attribute, dic[0], path)
    else:
      return False
      
  def set_attribute(self, attribute, value, path):
    '''
    Sets the value of a given attribute in a .jasmin file
    If the attribute exists, overrides the stored value.
    '''
    dic, jasmin_path = self.read_attributes(path)
    j_object = JasminFile(jasmin_path)
    dic = j_object.dictionary
    framework = j_object.framework
    dic[framework]['paths'][path][attribute] = value
    j_object.save()
    
    
    