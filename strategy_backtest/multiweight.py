from ..base.cnst import *
all_portfolio = {
	'S1801':{'S1801K':0.35,'S1501D2':0.30,'S1602B':0.35},
	'S1901':{'S1502C':0.70,'S1609A':0.30}
}
#############################################
def get_single_stra_position(stra):
	df = connBackTest.read('TradingDay,Symbol,Weight','alpha_strategy_daily_position','Strategy = %r'%stra)
	df = df.pivot('TradingDay','Symbol','Weight')
	return df

def all_stra_position(new_stra):
	add_portfolio = all_portfolio[new_stra]
	conbine_stras = list(add_portfolio.keys())
	conbine_stras_position = list(map(get_single_stra_position,conbine_stras))
	####################################
	all_tradingday = sorted(set.union(*map(lambda df:set(df.index),conbine_stras_position)))
	conbine_stras_position = list(map(lambda df:df_fillna_index(df,all_tradingday),conbine_stras_position))
	all_tradingday = sorted(set.intersection(*map(lambda df:set(df.index),conbine_stras_position)))
	conbine_stras_position = list(map(lambda df:df.reindex(all_tradingday) ,conbine_stras_position))
	##################################
	all_columns = sorted(set.union(*map(lambda df:set(df.columns),conbine_stras_position)))
	out_df = DataFrame(0,index = all_tradingday,columns = all_columns)
	for stra in conbine_stras:
		df = conbine_stras_position[conbine_stras.index(stra)].fillna(0)
		out_df.loc[df.index,df.columns] += add_portfolio[stra] * df
	return out_df

def weight_to_excel(dfc):
	df = dfc.copy()
	path = 'X:/BackTest/StrategyWeight/%s/W_%s_%s.xlsx' %(add_strategy,add_strategy,df['TradingDay'].unique()[0])
	df[['SecuCode','Weight']].to_excel(path, index=None)

def add_stra_to_excel(add_strategy):
	df = all_stra_position(add_strategy).tail(2)
	df = df.stack().reset_index()
	df.columns = ['TradingDay','SecuCode','Weight']
	df = df.query("Weight > 0.00001")
	df['TradingDay'] = df['TradingDay'].map(lambda k:k.strftime('%Y%m%d'))
	df['Weight'] *= 100
	df.groupby('TradingDay').apply(weight_to_excel)

for add_strategy in all_portfolio.keys():
	add_stra_to_excel(add_strategy)
	