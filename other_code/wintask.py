import os
import time

root_path = os.getcwd()
os.chdir(root_path)
multiweight_run = ['multiweight.py']
backtest_run = ['bt_data.py','bt_daily.py']
ams_run = ['ams_daily.py']
tick_run = ['bt_tick.py']

def run_task(all_task):
	for task_path in all_task:
		task_path = os.path.join(root_path,task_path)
		os.system(task_path)
	all_task = all_task if len(all_task) != 0 else 'goodbye,see you next day.'
	print('-\n'*3,'',all_task)
	time.sleep(300)

def which_task_to_run():
	cur_time = time.strftime('%H%M',time.localtime())
	if '0600' <= cur_time < '0607':
		run_task(backtest_run)
	elif '0700' <= cur_time < '0707':
		run_task(multiweight_run)
	elif '1640' <= cur_time < '1647':
		run_task(ams_run)
	elif '0930' <= cur_time < '0937':
		run_task(tick_run)
	elif '1650' <= cur_time:
		run_task([])
		return
	else:
		now = '%s:%s' %(cur_time[:2],cur_time[-2:])
		print('stephenliu: it is %s,waiting for next 5 minutes.'%now)
		time.sleep(300)
	which_task_to_run()

which_task_to_run()
