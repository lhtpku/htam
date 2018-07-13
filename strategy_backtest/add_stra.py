from ..base.cnst import *
path = 'add_stra.xlsx'
all_stra = pd.read_excel(path).fillna(' ')
print(all_stra)
connBackTest.delete_insert(all_stra,'strategy',['Strategy'])