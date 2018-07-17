import os,time

ROOT_PATH = 'X:/BackTest/StrategyWeight'
old_strategy = input('input old strategy: ')
new_strategy = input('input new strategy: ')
ROOT_PATH = os.path.join(ROOT_PATH,new_strategy)

all_file = [case for case in os.listdir(ROOT_PATH) if case.endswith('.xlsx')]
all_new_file = [case.replace(old_strategy,new_strategy) for case in all_file]

all_file = [os.path.join(ROOT_PATH,case) for case in all_file]
all_new_file = [os.path.join(ROOT_PATH,case) for case in all_new_file]

for i,file in enumerate(all_file):
	os.rename(file,all_new_file[i])

print('-----------------------')
print('updating name is ok!')
time.sleep(10)


