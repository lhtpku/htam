from basicpara import *
rootPath = '碎股清理/%s/' % Today
if os.path.exists(rootPath):
	shutil.rmtree(rootPath)
os.mkdir(rootPath)
#############################
Holding9997 = TotalHolding.query("Type == 'CS' and Strategy not in ('S0000','S0001','S9999','S9997')")
Holding9997 = Holding9997.query("AvailableQuantity == Quantity")
Holding9997['miniQuantity'] = Holding9997['Quantity'].map(lambda k:k % 100)
Holding9997 = Holding9997.query("miniQuantity > 0")
Holding9997 = Holding9997.sort_values(['PortfolioID','SecuCode','Quantity'], ascending=False)
Holding9997 = Holding9997.drop(['Type','Quantity','AvailableQuantity'], axis=1)
usePortfolio = sorted(Holding9997['PortfolioID'].unique())
######################################
def stockGather(df):
	df.index = list(range(len(df)))
	usePortfolio = df.ix[0,'PortfolioID']
	df['Direction'] = 'Sell'
	stockSum = df['miniQuantity'].sum()
	yuShu = stockSum % 100
	zhengShu = stockSum - yuShu
	if zhengShu > 0:
		df.loc['buy1',:] = [usePortfolio,df.ix[0,'Strategy'],df.ix[0,'SecuCode'],zhengShu,'Buy']
	if yuShu > 0:
		df.loc['buy2',:] = [usePortfolio,'S9997',df.ix[0,'SecuCode'],yuShu,'Buy']
	return df

def orderNormal2(df,totalCol = orderCol):
	df[totalCol[0]] = Today + '0000'
	df[totalCol[1]] = df['PortfolioID'].map(PortfolioMap)
	df[totalCol[2]] = df['PortfolioID'].map(AccountNoMap)
	df[totalCol[3]] = df['Strategy']
	df[totalCol[4]] = df['SecuCode'].map(lambda k:str(k).rjust(6,'0'))
	df[totalCol[5]] = '股票'
	df[totalCol[6]] = df['Direction'].map({'Sell':'卖出','Buy':'买入'})
	df[totalCol[7]] = df['Direction'].map({'Sell':'平仓','Buy':'开仓'})
	df[totalCol[8]] = df['miniQuantity']
	return df[totalCol]

def gatherMini(Port):
	df = Holding9997[Holding9997['PortfolioID'] == Port]
	df = df.groupby(df['SecuCode'],as_index = False).apply(stockGather)
	df.index = list(range(len(df)))
	outPath9997 = rootPath + PortfolioMap[Port] + '-碎股清理.xlsx'
	orderNormal2(df).to_excel(outPath9997,index = None)

list(map(gatherMini,usePortfolio))