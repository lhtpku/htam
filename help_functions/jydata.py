from .cnst import *
#######################################
SecuMarket = 'SecuMarket in (83,90)'
SecuCol = 'InnerCode,SecuCode,SecuAbbr,SecuCategory'
SecuStock = connJY.read(SecuCol,'SecuMain',"%s AND SecuCategory = 1 AND ListedDate<= %r" %(SecuMarket,TodayStr))
SecuIndex = connJY.read(SecuCol,'SecuMain',"SecuCategory = 4") ## 4为指数 8为开放式基金
SecuFund = connJY.read('InnerCode','SecuMain',"SecuCategory = 8")['InnerCode'].tolist()
Secu = pd.concat([SecuStock,SecuIndex],ignore_index = True)
####################################
mapChiName = TwoList(Secu['InnerCode'],Secu['SecuAbbr']).to_dict()
mapSecuType = TwoList(Secu['InnerCode'],Secu['SecuCategory']).to_dict()
SecuOld = connJY.read('InnerCode,SecuCode','LC_CodeChange','%s and CodeDefine = 1' %SecuMarket)
mapSecuCode = TwoList(SecuOld['InnerCode'],SecuOld['SecuCode']).to_dict()
mapSecuCode.update(TwoList(SecuStock['InnerCode'],SecuStock['SecuCode']).to_dict())
mapInnerCode = {value:key for key, value in list(mapSecuCode.items())}
mapIndexSecuCode = TwoList(SecuIndex['InnerCode'],SecuIndex['SecuCode']).to_dict()
mapIndexInnerCode = {value:key for key, value in mapIndexSecuCode.items()}
########################################
IndustryOld = PathIO(get_config_para('FilePath','old_industry')).read_df()
IndustryDict = TwoList(IndustryOld['Code'],IndustryOld['Industry']).to_dict()
IndustrySqlCol = 'a.InnerCode,a.SecuCode,b.FirstIndustryCode Industry,b.FirstIndustryName IndustryName'
IndustrySqlTable = 'SecuMain a inner join LC_ExgIndustry b on a.CompanyCode = b.CompanyCode'
IndustrySqlCondi = 'a.SecuMarket in (83,90) and a.SecuCategory = 1 and b.Standard = 24 and b.IfPerformed = 1'
IndustryTotal = connJY.read(IndustrySqlCol,IndustrySqlTable,IndustrySqlCondi)
IndustryDict.update(TwoList(IndustryTotal['InnerCode'],IndustryTotal['Industry']).to_dict())
IndustryChinese = TwoList(IndustryTotal['Industry'],IndustryTotal['IndustryName']).to_dict()
IndustryChinese.update({'Total':'汇总'})
############################################
def get_all_index_constitution(weight_start_date='20061001'):
	ALL_INDEX_str = ','.join(map(str,ALL_INDEX))
	useCol = 'IndexCode,InnerCode,EndDate TradingDay,Weight'
	useCondition = ["IndexCode in (%s)" %ALL_INDEX_str,"EndDate >= '%s'" %weight_start_date]
	sql = SqlSelect('LC_IndexComponentsWeight').condition_select(useCol,useCondition)
	######################################
	index_constitution = connJY.read_by_sql(sql)
	index_constitution['Weight'] = index_constitution['Weight']/100
	index_constitution['TradingDay'] = index_constitution['TradingDay'].map(pd.to_datetime)
	index_constitution = index_constitution.set_index(['IndexCode','TradingDay']).sort_index()
	index_weightDate = [sorted(list(index_constitution.loc[k,:].index.unique())) for k in ALL_INDEX]
	map_index_to_weightDate = TwoList(ALL_INDEX,index_weightDate).to_dict()
	return index_constitution, map_index_to_weightDate
index_constitution,map_index_to_weightDate = get_all_index_constitution()
#####################################################
def get_index_constitution_someday(day,idx):
	use_day = map_index_to_weightDate[idx]
	index_constitution_someday = index_constitution.loc[(idx,MyList(use_day).get_latest_element(day)),:]
	return index_constitution_someday['InnerCode'].tolist()

def get_index_constitution_weight_someday(day,idx):
	use_day = map_index_to_weightDate[idx]
	index_constitution_someday = index_constitution.loc[(idx,MyList(use_day).get_latest_element(day)),:]
	return index_constitution_someday['InnerCode','Weight']


def get_index_constitution(day):
	tmp = [get_index_constitution_someday(day,k) for k in ALL_INDEX]
	return dict(list(zip(ALL_INDEX,tmp)))
