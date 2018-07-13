from .multistra import *

def single_strategy_calculate(Strategy):
	if (Strategy not in only_return_strategy):
		strategy_position_class = StrategyWeight(Strategy)
		for path in strategy_position_class.file_path[-1:]:
			strategy_position_class.insert_to_db([path],['Strategy','TradingDay'])
	daily_return_class = DailyReturn(Strategy)
	daily_return_class.return_insert()
	if eval(YesterdayStr[-1])%4 == 1:
		daily_return_class.insert_industry_grade()
##########
config_stra = get_config_para('RunStrategy','daily_stra')
daily_run_strategy = config_stra if len(config_stra) > 0 else full_strategy[:]
for i,Strategy in enumerate(daily_run_strategy[:]):
	single_strategy_calculate(Strategy)
####################################################
if len(config_stra) >= 1:
	logging.info('temp updating is ok.')
	time.sleep(60)
	raise SystemExit('temp updating is ok.')
################################
class_full_strategy().main_run()
########
from lht.btdata.risk import *
POSITION = BTData()
POSITION.main_run()
logging.info('updating daily risk in %s is ok.' %YesterdayStr)
####################################################
logging.critical("Updating backtest data in %s is ok." %YesterdayStr)
connBackTest.close_db()
time.sleep(60)
