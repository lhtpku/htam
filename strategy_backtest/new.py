from .multistra import *
config_stra = get_config_para('RunStrategy','new_stra')
new_strategy = config_stra if len(config_stra) > 0 else new_strategy[:]
print('new strategy:', new_strategy)
######################################
for Strategy in new_strategy[:]:
	logging.info('start creating strategy %s'%Strategy)
	if Strategy not in only_return_strategy:
		strategy_position_class = StrategyWeight(Strategy)
		temp_path = strategy_position_class.file_path[:]
		strategy_position_class.insert_to_db(temp_path,['Strategy'])
	daily_return_class = DailyReturn(Strategy)
	daily_return_class.return_insert()
	daily_return_class.insert_industry_grade()
	logging.critical("Creating backtest data of %s is ok."%Strategy)
####################################
class_full_strategy().main_run()
connBackTest.close_db()
time.sleep(60)



























