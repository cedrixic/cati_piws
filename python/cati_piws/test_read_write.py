# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 11:56:21 2016

@author: cc247755
"""

from __future__ import print_function
#import six
import os
#import os.path as osp
#import sys
import json
import jasmin
from bz2 import BZ2File
import unittest
from tempfile import mkdtemp
import shutil


class TestJasminIO(unittest.TestCase):
  '''
  Test class for jamsin files and attributes handling
  '''
  
  def touch(self, path):
    with open(path, 'a'):
        os.utime(path, None)
          
  def setUp(self):
    '''   
    Setting up temp path and files for test
    '''

    # Temporary data arborescence base dir
    self.dir1test = mkdtemp('','test_jasminIO_')
#    print('tmpdir1 : ', self.dir1test)
    self.dir2test = self.dir1test + '/subject1/'
    self.dir3test = self.dir1test + '/subject1/modality1/'
    self.dir4test = self.dir1test + '/subject1/modality2/'
    os.makedirs(self.dir2test)
    os.makedirs(self.dir3test)
    os.makedirs(self.dir4test)
    
#    print('dir2test : ', self.dir2test)
#    print('dir3test : ', self.dir3test)
#    print('dir4test : ', self.dir4test)
    
    # Temporary images and files
    #
    # file2write : image exists, jasmin file is created
    # file2readRecurs : image exists, but file.ima.jasmin file is not attached
    #   to the file; 'path' attributes are defined in a .jasmin file, located
    #   in the study root directory
    # file2readRecursFalse : image exists, attributes are not defined anywhere
    # dictRecursPath : common .jasmin file, located at the root directory
    
    self.file2write = self.dir3test + 'image1.ima'
    self.file2readRecurs = self.dir3test + 'image2.ima'
    self.file2readRecursFalse = self.dir4test + 'image1.ima'
    self.dictRecursPath = self.dir1test + '/.jasmin'
    self.touch(self.file2write)
    self.touch(self.file2readRecurs)
    self.touch(self.file2readRecursFalse)
    
#    print('file2write : ', self.file2write)
#    print('file2readRecurs : ', self.file2readRecurs)
#    print('file2readRecursFalse : ', self.file2readRecursFalse)
    
    # Attributes to write/to get
    self.test_framework = 'framework' 
    self.test_center = 'Test center' 
    self.test_action = 'Test action'    
    self.test_subject = 'Test subject'    
    self.test_modality = 'Test modality' 
    self.attributeToGet = 'center_uuid'  
    self.attributeToSet = 'attribute_set_test' 
    self.valueToSet = 'Test set attribute ok'
    self.attributeToReplace = 'modality'
    self.valueToReplace = 'Test attribute to replace ok'
    
#    Temporary dictionaries
    self.dictRecurs={}
    self.dictRecurs[self.test_framework] = {}
    self.dictRecurs[self.test_framework]["paths"] = {}
    self.dictRecurs[self.test_framework]["paths"][self.file2readRecurs] = {}
    self.dictRecurs[self.test_framework]["paths"][self.file2readRecurs]\
                   ["generated_by_action"] = self.test_action
    self.dictRecurs[self.test_framework]["paths"][self.file2readRecurs]\
                   ["center_uuid"] = self.test_center
    self.dictRecurs[self.test_framework]["paths"][self.file2readRecurs]\
                   ["subject_uuid"] = self.test_subject
    self.dictRecurs[self.test_framework]["paths"][self.file2readRecurs]\
                   ["modality"] = self.test_modality
    
    json.dump(self.dictRecurs, BZ2File(self.dictRecursPath,'w'))
    
    
    self.dic2write={}
    self.dic2write[self.test_framework] = {}
    self.dic2write[self.test_framework]["paths"] = {}
    self.dic2write[self.test_framework]["paths"][self.file2write] = {}
    self.dic2write[self.test_framework]["paths"][self.file2write]\
                  ["generated_by_action"] = self.test_action
    self.dic2write[self.test_framework]["paths"][self.file2write]\
                  ["center_uuid"] = self.test_center
    self.dic2write[self.test_framework]["paths"][self.file2write]\
                  ["subject_uuid"] = self.test_subject
    self.dic2write[self.test_framework]["paths"][self.file2write]\
                  ["modality"] = self.test_modality
    
    
  def tearDown(self):
    '''   
    Clean-up of temporary directory
    '''
    shutil.rmtree(self.dir1test)
    
    
  def test_ReadWriteAttributes(self):
    '''   
    Testing read/write attributes function (whole dictionary processing)
    '''
    
#    Jasmin file access instance
    j_access = jasmin.JasminIO()
    
#    Testing write_attributes function
    self.assertEqual(
      j_access.write_attributes(self.file2write, self.dic2write),True)

#    Testing read_attributes function in an attached .jasmin file      
    (dicRes, jasmin_path) = j_access.read_attributes(self.file2write)    
    self.assertEqual(dicRes == self.dic2write[self.test_framework]\
                     ['paths'][self.file2write], True)
      
#    Testing read_attributes function in a root .jasmin file      
    (dicRes, jasmin_path) = j_access.read_attributes(self.file2readRecurs)
    self.assertEqual(dicRes == self.dictRecurs[self.test_framework]\
                     ['paths'][self.file2readRecurs], True)
      
#    Testing read_attributes function behavior for path 
#    not stored in any .jasmin file
    self.assertEqual(
      j_access.read_attributes(self.file2readRecursFalse), False)
      
  def test_GetSetSingleAttribute(self):
    '''   
    Testing get/set_attribute function (single attribute value)
    '''
#    Jasmin file access instance
    j_access = jasmin.JasminIO()     


#    Write jasmin file from a dictionary
    if j_access.write_attributes(self.file2write, self.dic2write) :
      
#      Test if attribute can be reached
      self.assertEqual( j_access.get_attribute(self.attributeToGet, 
                       self.file2write),self.test_center)
                       
#      Test if new attribute can be set and correctly read
      j_access.set_attribute( self.attributeToSet, 
                              self.valueToSet, 
                              self.file2write)
      self.assertEqual( j_access.get_attribute(self.attributeToSet, 
                       self.file2write),self.valueToSet)
                       
#      Test if attribute value can be replaced and correctly read
      j_access.set_attribute( self.attributeToReplace, 
                              self.valueToReplace, 
                              self.file2write)
      self.assertEqual( j_access.get_attribute(self.attributeToReplace, 
                       self.file2write),self.valueToReplace)
                               
#      Test if attribute value can be read in a root .jasmin file
    self.assertEqual(
      j_access.get_attribute(self.attributeToGet, 
                             self.file2readRecurs),self.test_center)
                             
#      Test behavior when trying to reach a non existing attribute
    self.assertEqual(
      j_access.get_attribute(self.attributeToGet, 
                             self.file2readRecursFalse),False)


def test():
    """ Function to execute unitest
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestJasminIO)
    runtime = unittest.TextTestRunner(verbosity=2).run(suite)
    return runtime.wasSuccessful()
    
if __name__ == '__main__':
    print("RETURNCODE: ", test())








#    print('\n')
#    if dicRes != False :
#      for i in dicRes.items():
#        print('Key : ', i[0], ' - Value : ', i[1])
#    else :
#      print('no jasmin file found!!')

#  def test_Get_Attribute(self):
#    j_access = jasmin.JasminIO()
#    print('Test with existing attribute :')
#    attr = j_access.get_attribute(self.attributeToGet, self.file2read)
#    if attr is False :
#      print('no jasmin file or path in dictionary')
#    else :
#      if attr is None :
#        print('Attribute not found in dictionary')
#      else :
#        print('Read attribute : ', self.attributeToGet, ' : ', attr)
#    
    