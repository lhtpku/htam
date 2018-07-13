from .var import *
HdfIndustryDict = dict(zip(BenchmarkName,['Industry46','Industry3145','Industry4978']))
HdfMvDict = dict(zip(BenchmarkName,['Grade46','Grade3145','Grade4978']))
#############################
total_h5_path = get_config_para('FilePath','h5_path')
total_pct_h5_path = total_h5_path + 'DailyQuote%s.h5' %YesterdayStr
total_factor_h5_path = total_h5_path + 'Factor%s.h5' %YesterdayStr
##########################################
total_pct_h5 = pd.HDFStore(total_pct_h5_path)
total_pct = total_pct_h5['ClosePct']
total_factor_h5 = pd.HDFStore(total_factor_h5_path)

def get_factor_data_from_h5(factor,idx):
	key = '%s/Index%s/allyear' %(factor,idx)
	return total_factor_h5[key]
