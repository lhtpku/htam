# -*- coding: utf-8 -*- 
import os
root_path = os.getcwd()
os.chdir(root_path)
target_dir = os.path.join(root_path,'pool')
#################################
def py2_to_py3():  
    all_py_file = [os.path.join('pool',file) for file in os.listdir(target_dir) if file.endswith('.py')]
    for path in all_py_file:  
        cmd_order = '%s -w %s'%('2to3.py', path)
        os.system(cmd_order)

if __name__ == '__main__':
     py2_to_py3()
