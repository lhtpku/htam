import os
import time
import shutil
import numpy as np
import pandas as pd
from pandas import Series,DataFrame
from datetime import datetime
import pandas.tseries.offsets as offsets
import MySQLdb
use_date_str = (datetime.today() + offsets.BusinessDay(-1)).strftime('%Y%m%d')
# use_date_str = '20180615'
print(use_date_str)
new_valuation_path = 'Z:/DailyReport/DailyValuation/%s' % use_date_str
if os.path.exists(new_valuation_path):
    shutil.rmtree(new_valuation_path)
today_str = datetime.today().strftime('%Y%m%d')
old_valuation_path = os.path.join('H:/temp/YSSGZ/估值表晚班',today_str[:4],today_str[2:6],use_date_str[2:])
shutil.copytree(old_valuation_path,new_valuation_path)
###########################################
valuation_path_end = '%s估值表量化投资部.xlsx' %use_date_str

class AccountAsset(object):
    def __init__(self):
        self.all_valuation_path()
        self.all_account_share()
        self.main_run()

    def get_valuation_path(self,account):
        path = os.path.join(new_valuation_path,account + valuation_path_end)
        return path

    def is_file_exists(self,path):
        if os.path.exists(path):
            return True
        print('path do not exists.')
        print(path)
        return False

    def all_valuation_path(self):
        self.BianHaoID = dict()
        Path70 = self.get_valuation_path('1018量化####')
        Path71 = self.get_valuation_path('1031量化####')
        self.BianHaoID = {Path70:70, Path71:71, Path72:72, Path69:69, Path79:79, Path80:80}
        self.BianHaoID.update({Path81: 81, Path82: 82, Path85: 85})
        self.BianHaoID.update({Path75:75,Path76:76})
        # self.BianHaoID.update({Path92:92,Path93:93,Path94:94})
        # self.BianHaoID.update({Path95:95})
        self.BianHaoID.update({Path98:98,Path99:99,Path100:100})
        self.BianHaoID.update({Path101:101,Path102:102,Path103:103})
        self.BianHaoID.update({Path107:107,Path108:108,Path109:109})
        self.BianHaoID.update({Path200:130})
        self.A_P = {value:key for key,value in list(self.BianHaoID.items())}

    def all_account_share(self):
        self.share_dict = {}
        self.share_dict[69] = 100000000
        self.share_dict[75] = 176770000
        # self.share_dict[111] = 171819735
        for Account in list(self.A_P.keys()):
            if Account in [69,75,76]:
                continue
            if not self.is_file_exists(self.A_P[Account]):
                continue
            self.share_dict[Account] = self.normal_account(Account,share=True)
        self.share_dict = DataFrame(self.share_dict,index = [0]).T
        share_path = os.path.join(new_valuation_path,'ShareTable.csv')
        self.share_dict.to_csv(share_path,header=None)

    def equity_account(self):
        self.result = dict()
        equity_account_id = [104,105,106] + list(range(112,126))
        equity_account_asset = [188976,88699,192921,37364,98327,11303,31148,36978,29591,14976]
        equity_account_asset.extend([14964,15934,15889,105582,18729,50528,108399])
        equity_account_asset = [10000*k for k in equity_account_asset]
        for i in range(len(equity_account_id)):
            self.result[equity_account_id[i]] = [equity_account_asset[i],1]

    def get_value(self,df,ID):
        try:
            return df.ix[ID,'市值']
        except KeyError:
            return 1.0

    def get_75(self,path):
        return 1.0134*176770000,1.0134
        GuZhi = pd.read_excel(path).set_index('单元序号')
        TotalValue = GuZhi.loc[1729,'资产净值（净价）'] + GuZhi.loc[1741,'资产净值（净价）']
        TotalValue += (1402838 + 1578600 - 79000)
        TotalValue += 5064934.75 #### 2017-09-13 资金从固收
        TotalValue -= 2350000 #### 2017-11-02 调整备付金235万
        TotalValue -= 2350000 #### 2018-02-02 调整备付金235万
        if use_date_str == '20180301':
            TotalValue = 1.0163 * 176770000
        PerValue = (TotalValue) / 176770000
        return TotalValue,PerValue

    def get_76(self,path):
        return 100000,0.001
        GuZhi = pd.read_excel(path).set_index('单元序号')
        TotalValue = GuZhi.loc[1761,'资产净值（净价）']
        PerValue = TotalValue / (161744413 - 54774511.6)
        return TotalValue,PerValue

    def get_69(self,path=''):
        TotalValue = 105610000.0
        PerValue = TotalValue / 100000000
        return TotalValue,PerValue

    def in_case_wrong(self,Account):
        if Account == 75:
            func = self.get_75
        elif Account == 76:
            func = self.get_76
        elif Account == 69:
            func = self.get_69
        path = self.A_P[Account] if Account != 69 else ''
        try:
            return func(path)
        except:
            print('something is wrong:')
            print(path)
            return 1e8,1.0000

    def normal_account(self,Account,share = False):
        GuZhi = pd.read_excel(self.A_P[Account])
        GuZhi.index = list(range(len(GuZhi)))
        try:
            GuZhi = GuZhi.set_index('科目代码')
            if share == True:
                if Account == 101:
                    return self.get_value(GuZhi,'实收基金')
                return self.get_value(GuZhi,'实收资本')
            TotalValue = self.get_value(GuZhi,'委托资产净值:')
            PerValue = self.get_value(GuZhi,'今日单位净值:')
            return TotalValue,PerValue
        except ValueError:
            print('something is wrong:')
            print(A_P[Account])
            if share == True:
                return 1e8
            return 1e8,1.0000

    def main_run(self):
        self.equity_account()
        for Account in list(self.A_P.keys()):
            if (not self.is_file_exists(self.A_P[Account])) & (Account not in [75,76,69]):
                continue
            if Account in [75,76,69]:
                TotalValue,PerValue = self.in_case_wrong(Account)
                self.result[Account] = [int(TotalValue),round(PerValue,4)]
            else:
                TotalValue,PerValue = self.normal_account(Account)
            self.result[Account] = [int(TotalValue),round(PerValue,4)]
        RESULT = DataFrame(self.result).T.rename(columns={0: 'TotalValue', 1: 'PerValue'})
        RESULT = RESULT.reset_index()
        PATH = '%s/%s.csv'%(new_valuation_path,use_date_str)
        RESULT.to_csv(PATH, header=None, index=None)
        print(RESULT)
        print('\n'.join(3*['----------------']))
        print(len(RESULT))
        self.insert_value()
        print('inserting to db is ok.')
        print('\n'.join(3*['----------------']))

    def insert_value(self):
        net_value = pd.read_csv('%s/%s.csv'%(new_valuation_path,use_date_str),header=None)
        net_value.loc[:,3] = net_value[2]
        net_value.insert(1,'Date',use_date_str)
        net_value.columns = ['PortfolioID','Date','Value','PerValue','PerValue2']
        self.insert_sql(net_value)

    def insert_sql(self,df):
        conn = MySQLdb.connect(host = '10.248.25.11',user = 'root',passwd = 'root',port = 8908,db = 'algodb')
        cur = conn.cursor()
        if_duplicate_sql = "delete from portfolio_performance WHERE TradeDate = %r" %use_date_str
        cur.execute(if_duplicate_sql)
        insert_sql = '''
        insert into portfolio_performance (PortfolioID,TradeDate,NetValue,UnitNV,AccumulatedUnitNV) VALUES (%s,%s,%s,%s,%s)
        '''
        cur.executemany(insert_sql,list(map(list,df.values)))
        conn.commit()
        conn.close()


AccountAsset()