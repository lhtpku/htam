library(xlsx)
library(ggplot2)
library(Cairo)
library(showtext)
library(grid)
library(reshape2)
library(scales)
library(gridExtra)


source('E:/RMD20170406/useFunctions.r',encoding="utf-8")

RiskPath = paste('DailyRisk',Today,'-.xlsx',sep = '')



WriteRoot = 'X:/每日策略检查/每日日报/'

WritePath = paste(WriteRoot,Today,'/','Risk',Today,'.pdf',sep = '')

WeightRisk = ReadExcel('E:/RMD20170406/WeightDelta20170407.xlsx',1,T)
AlphaRisk = ReadExcel('E:/RMD20170406/IndustryAlpha20170407.xlsx',1,T)


#cairo_pdf(WritePath,width=15/2.54,height=20/2.54,family='GB1')
pdf(WritePath,width=15/2.54,height=20/2.54,family='GB1')

Path = getPath('兴业')


deltaGraph = function(Total,Accou,Col,HedgeType,TitleName){
  df1 = getSplitData(Total,Accou,Col)
  df2 = getSplitData(df1,HedgeType,c(2:3))
  Graph = BarGraph(df2,1.5,7,5,TitleName)
  return (Graph)
}




showtext.begin()
vplayout = function(x,y)
  viewport(layout.pos.row=x,layout.pos.col=y)


grid.newpage()
pushViewport(viewport(layout=grid.layout(4,2)))

AA1 = getSplitData(ReadExcel(Path,4,F),'策略仓位结构',c(2:3))
AA1 = BarGraph(AA1,1.5,7,5,'兴业一号 策略仓位')
BB1 = getSplitData(ReadExcel(Path,4,F),'对冲策略仓位',c(2:3))
BB1 = BarGraph(BB1,1.5,7,5,'兴业一号 Alpha策略仓位')

WeightRisk1_300 = deltaGraph(WeightRisk,'XingYe_I',c(2:4),'对冲300','兴业一号 对冲300策略行业偏配(前五&后五)')
WeightRisk1_500 = deltaGraph(WeightRisk,'XingYe_I',c(2:4),'对冲500','兴业一号 对冲500策略行业偏配(前五&后五)')
WeightRisk1_50 = deltaGraph(WeightRisk,'XingYe_I',c(2:4),'对冲50','兴业一号 对冲50策略行业偏配(前五&后五)')

alphaRisk1_300 = deltaGraph(AlphaRisk,'XingYe_I',c(2,3,5),'对冲300','兴业一号 对冲300策略行业Alpha(前五&后五)')
alphaRisk1_500 = deltaGraph(AlphaRisk,'XingYe_I',c(2,3,5),'对冲500','兴业一号 对冲500策略行业Alpha(前五&后五)')
alphaRisk1_50 = deltaGraph(AlphaRisk,'XingYe_I',c(2,3,5),'对冲50','兴业一号 对冲50策略行业Alpha(前五&后五)')

print(AA1,vp=vplayout(1,1))
print(BB1,vp=vplayout(1,2))
print(WeightRisk1_300,vp=vplayout(2,1))
print(alphaRisk1_300,vp=vplayout(2,2))
print(WeightRisk1_500,vp=vplayout(3,1))
print(alphaRisk1_500,vp=vplayout(3,2))
print(WeightRisk1_50,vp=vplayout(4,1))
print(alphaRisk1_50,vp=vplayout(4,2))
#grid.arrange(AA1,BB1,WeightRisk1_300,alphaRisk1_300,WeightRisk1_500,alphaRisk1_500,WeightRisk1_50,alphaRisk1_50,ncol=2,nrow=4,widths=c(1,1),heights=c(1,1,1,1))

showtext.end()

#dev.new()
showtext.begin()
grid.newpage()
pushViewport(viewport(layout=grid.layout(4,2)))


AA2 = getSplitData(ReadExcel(Path,7,F),'策略仓位结构',c(2:3))
AA2 = BarGraph(AA2,1.5,7,5,'兴业二号 策略仓位')
BB2 = getSplitData(ReadExcel(Path,7,F),'对冲策略仓位',c(2:3))
BB2 = BarGraph(BB2,1.5,7,5,'兴业二号 Alpha策略仓位')

WeightRisk2_300 = deltaGraph(WeightRisk,'XingYe_II',c(2:4),'对冲300','兴业二号 对冲300策略行业偏配(前五&后五)')
WeightRisk2_500 = deltaGraph(WeightRisk,'XingYe_II',c(2:4),'对冲500','兴业二号 对冲500策略行业偏配(前五&后五)')
WeightRisk2_50 = deltaGraph(WeightRisk,'XingYe_II',c(2:4),'对冲50','兴业二号 对冲50策略行业偏配(前五&后五)')

alphaRisk2_300 = deltaGraph(AlphaRisk,'XingYe_II',c(2,3,5),'对冲300','兴业二号 对冲300策略行业Alpha(前五&后五)')
alphaRisk2_500 = deltaGraph(AlphaRisk,'XingYe_II',c(2,3,5),'对冲500','兴业二号 对冲500策略行业Alpha(前五&后五)')
alphaRisk2_50 = deltaGraph(AlphaRisk,'XingYe_II',c(2,3,5),'对冲50','兴业二号 对冲50策略行业Alpha(前五&后五)')


print(AA2,vp=vplayout(1,1))
print(BB2,vp=vplayout(1,2))

print(WeightRisk2_300,vp=vplayout(2,1))
print(alphaRisk2_300,vp=vplayout(2,2))

print(WeightRisk2_500,vp=vplayout(3,1))
print(alphaRisk2_500,vp=vplayout(3,2))

print(WeightRisk2_50,vp=vplayout(4,1))
print(alphaRisk2_50,vp=vplayout(4,2))



showtext.end()
dev.off()


