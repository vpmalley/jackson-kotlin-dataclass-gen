#! /usr/bin/env python

import json
import sys
import os

# constants and default values
default_package = 'com.example';
default_visibility = '';
default_indent = '    '; # four spaces

beans_dir = 'model/';
file_ext = '.kt'
sep = '\n';
package_prefix = 'package ';
package_suffix = '\n\n';
default_imports = ['import io.realm.RealmObject\n']
import_string_line = '';
import_list_line = 'import io.realm.RealmList\n';
class_prefix = '\nopen class ';
class_suffix = ' : RealmObject() {\n';
class_end = '\n}'


# Retrieves the file located at <beanFile>
# @param beanFile the path (relative or absolute) to the sample bean file. It must be a json file
# @param beanName the name of the bean, used to generate a java file
def generateBean(beanFile, beanName):
  # loading the sample bean from file
  beanF = open(beanFile, 'r');
  sampleBean = json.load(beanF);
  beanF.close();
  visitAndPrintBean(beanName, sampleBean);



# Visits the whole bean and generates a java file. Visits embedded beans as well.
# @param beanName the name of the bean, formatted as a Java class name (i.e. its first letter capitalized)
# @param sampleBean the object to visit (either an object or a list, other types are not handled)
def visitAndPrintBean(beanName, sampleBean):
  beanDesc = '';
  imports = [];
  if type(sampleBean) is dict:
    for key in sampleBean.keys():
      beanType = getType(key, sampleBean[key]);
      # constructing the member line
      beanDesc += default_indent + memberVisibility + ' var ' + key + ': ' + beanType['type'] + ' = ' + beanType['defaultValue'] + sep;

      # adding all imports of the bean to the global imports, removing duplicates along the way
      for import_line in beanType['imports']:
        if import_line not in imports:
          imports.append(import_line);

  elif type(sampleBean) is list:
    if not sampleBean: # if the array is empty
      print 'This looks like an empty array';
      return;
    else:
      # assumption : all items of an array have the same structure
      visitAndPrintBean(beanName, sampleBean[0]);
      return;
  else :
    print 'This looks like a straightforward json/Java type: ' + type(sampleBean);
    return;

  import_lines = '';
  for import_line in imports:
    import_lines += import_line


  # constructing the file as a list of lines:
  # package, imports, opening class, class body, closing class
  beanFileContent = package_prefix + package + package_suffix + import_lines + class_prefix + beanName + class_suffix + beanDesc + class_end;


  # writing to the file
  filePath = beans_dir + beanName + file_ext;
  beanF = open(filePath, 'w');
  beanF.write(beanFileContent);
  beanF.close();
  print '  generated bean ' + beanName + ' to file ' + filePath;



# Determines the type of an element
# @param key the name of the element
# @param sampleElement the value of the element
# @return an object containing
#  - type, a string indicating the java type
#  - imports, an array of strings containing the import lines to add to the java file
def getType(key, sampleElement):
  elementType = '';
  imports = default_imports;
  if type(sampleElement) is dict: # the member type is a lower level bean
    visitAndPrintBean(key.capitalize(), sampleElement);
    elementType = key.capitalize();
    defaultValue = key.capitalize() + '()';
  elif type(sampleElement) is list:
    if not sampleElement: # if the array is empty
      elementType = 'List<Any>';
    else:
      # assumption : all items of an array have the same structure
      listType = getType(key, sampleElement[0]);
      elementType = 'RealmList<' + listType['type'] + '>';
      imports.extend(listType['imports']);
    imports.append(import_list_line);
    defaultValue = 'RealmList()'
  elif type(sampleElement) is unicode:
    elementType = 'String';
    imports.append(import_string_line);
    defaultValue = '""'
  elif type(sampleElement) is int:
    elementType = 'Int';
    defaultValue = '0'
  elif type(sampleElement) is float:
    elementType = 'Double';
    defaultValue = '0.0'
  elif type(sampleElement) is bool:
    elementType = 'Boolean';
    defaultValue = 'false'
  else :
    elementType = 'Any';
  return { 'type' : elementType, 'imports' : imports, 'defaultValue' : defaultValue};



# prints the help
def printHelp():
  print '\n  This script builds Kotlin data classes from the beans in a sample json file.\n';
  print '  It accepts some arguments, including one mandatory:\n';
  print '   - (mandatory) sampleFile the path to the sample json file (including the extension)';
  print '   - (optional) package the package for the generated classes. Default: com.example'
  print '   - (optional) beanName the name of the top-level object. Default: the name of the json file is used'
  print '   - (optional) memberVisibility the visibility of the members of the classes (private, protected, default or public). Default: private'





####
# the script

# print help if no argument passed
if len(sys.argv) < 2:
  printHelp();
  exit();


# default values
beanName = sys.argv[1].partition('.')[0].capitalize();
memberVisibility = default_visibility;
package = default_package;

if (len(sys.argv) > 2):
  package = sys.argv[2];

if (len(sys.argv) > 3):
  beanName = sys.argv[3].capitalize();

if (len(sys.argv) > 4):
  memberVisibility = sys.argv[4];

# create dir for results
if not os.path.exists(beans_dir):
    os.makedirs(beans_dir);
# generate all beans defined in the file passed as first argument and generate a java file with the bean name <beanName>
generateBean(sys.argv[1], beanName);
