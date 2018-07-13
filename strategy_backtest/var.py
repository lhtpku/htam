from ..base.jydata import *
BenchmarkName = [50,300,500,1000,120]
BenchmarkIndex1 = ['000016.SH','000300.SH','000905.SH','000852.SH','CES120.CSI']
BenchmarkIndex2 = ['H00016.SH','H00300.CSI','H00905.CSI','000852.SH','CES120.CSI']
BenchmarkDict = dict(list(zip(BenchmarkName,BenchmarkIndex2)))
############################################
StrategyWeightRootPath = get_config_para('FilePath','stra_weight')
all_strategy_attri = StrategyProperty(connBackTest,TodayStr)
all_strategy = all_strategy_attri.all_strategy()
full_strategy = all_strategy_attri.full_strategy()
strategy_status = all_strategy_attri.strategy_status()
only_return_strategy = all_strategy_attri.only_return_strategy()
new_strategy = all_strategy_attri.new_strategy()
##############################################
all_strategy_attri_col = ['BenchMark',
						'IsTiming',
						'IsIndex',
						'IsBeta',
						'IsLongShort',
						'IsOnlyReturn',
						'SellingTime',
						'IsMixHedge']
all_strategy_dict = [all_strategy_attri.strategy_attri(col) for col in all_strategy_attri_col]
###
[strategy_bench_dict,
strategy_timing_dict,
strategy_index_dict,
strategy_beta_dict,
strategy_longshort_dict,
strategy_onlyreturn_dict,
strategy_sellingtime_dict,
strategy_mixhedge_dict] = all_strategy_dict