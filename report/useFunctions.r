Today = format(Sys.Date(),'%Y%m%d')

RootPath = paste("X:/每日策略检查/每日日报/",Today,"/",sep ="")


getPath = function(Accou){
  return (paste(RootPath,Today,Accou,'.xls',sep = ''))
}


ToPercent = function(k){
  mm = paste(round(as.numeric(k)*100,2),'%',sep="")
  return (mm)
}

ToDigit4 = function(k){
  mm = as.numeric(k)
  return (sprintf("%.4f",mm))
}



ReadExcel = function(usePath,Index,Header){
  dd = data.frame(read.xlsx(usePath,sheetIndex = Index,header = Header,encoding = 'UTF-8'))
  return (dd)
}


ReadExcelName = function(usePath,Name,Header){
  dd = data.frame(read.xlsx(usePath,sheetName = Name,header = Header,encoding = 'UTF-8'))
  return (dd)
}



BarGraph = function(df,LabelSize,TitleSize,XSize,TITLE){
  colnames(df) = c('class','data')
  WriteLable = paste(round(df$'data'*100,2),'%',sep="")
  df$obj = factor(df$class,levels = df$class)
  if (sum(df$data) == 0){
    GraphOut = ggplot() + labs(title = TITLE) + 
      theme(plot.title = element_text(size=TitleSize,colour = "black",face = "plain")) +
      theme(plot.title = element_text(hjust = 0.5))
  }
  else {
  GraphOut = ggplot(df,aes(x=df$obj,y=df$data)) + 
    geom_bar(stat='identity',position='identity',fill='grey',colour='grey',width=0.25)+ 
    geom_text(aes(label=WriteLable),vjust=0.3,colour='black',size=LabelSize) +
    scale_y_continuous(breaks=NULL)+
    ylab("")+ xlab("")+ labs(title = TITLE)+
    geom_hline(yintercept=0)+
    theme(plot.title = element_text(size=TitleSize,colour = "black",face = "plain"))+
    theme(axis.ticks = element_blank(),axis.text.y=element_blank())+
    theme(axis.text.x = element_text(angle=30,size=XSize,hjust=1,vjust=1),panel.grid.major = element_blank())+
    theme(plot.title = element_text(hjust = 0.5))
  }
  return (GraphOut)}



BarGraph2 = function(df,TitleSize,XSize,TITLE){
  colnames(df) = c('class','data')
  #df$'class'
  df$obj = factor(df$class,levels = df$class)
  if (sum(df$data) == 0){
    GraphOut = ggplot() + labs(title = TITLE) + 
      theme(plot.title = element_text(size=TitleSize,colour = "black",face = "plain")) + 
      theme(plot.title = element_text(hjust = 0.5))
  }
  else {
    GraphOut = ggplot(df,aes(x=df$obj,y=df$data)) + 
    geom_bar(stat='identity',position='identity',fill='grey',colour='grey',width=0.25)+ 
    scale_y_continuous(breaks=NULL)+
    ylab("")+ xlab("")+ labs(title = TITLE)+
    geom_hline(yintercept=0)+
    theme(plot.title = element_text(size=TitleSize,colour = "black",face = "plain"))+
    theme(axis.ticks = element_blank(),axis.text.y=element_blank())+
    theme(axis.text.x = element_text(angle=30,size=XSize,hjust=1,vjust=1),panel.grid.major = element_blank())+
    theme(plot.title = element_text(hjust = 0.5))
  }
  return (GraphOut)}








getSplitData = function(df,Type,Col) {
  df1 = df[df[,1] == Type,]
  return (df1[,Col])
}




NetvalueGraph = function(df,StartDate,Frequen,TITLE,TitleSize,YSize){
  colnames(df)=c('date','NetValue')
  df['Date'] = as.Date(df$date)
  df = df[complete.cases(df),]
  MaxValue = round(max(df$NetValue),4)
  MinValue = round(min(df$NetValue),4)
  AbsMax = MaxValue
  
  if (AbsMax > 1.1) {kk = 0.0500}
  
  else if (1.05< AbsMax & AbsMax <= 1.1) {kk = 0.02}
  
  else if (1.01< AbsMax & AbsMax <= 1.05) {kk = 0.01}

  else {kk = 0.00200}
  
  pp = seq(1,MaxValue,by = kk)
  
  datebreaks = seq(as.Date(StartDate),as.Date(Sys.Date()),by=Frequen)
  
  AA = 
    ggplot(df,aes(x=df$Date,y=df$NetValue,group=1)) + geom_line() +
    labs(x ='',y ='', title = TITLE)+ geom_hline(yintercept=1)+
    theme(panel.grid.major = element_blank())+theme(axis.ticks = element_blank())+
    theme(plot.title = element_text(size=TitleSize,colour = "black",face = "plain"))+
    theme(axis.text.x = element_text(angle=45,size=YSize),panel.grid.major = element_blank())+
    scale_x_date(breaks=datebreaks,label = date_format('%Y-%m-%d')) + 
    scale_y_continuous(labels=round(pp,4),breaks=pp)+
    theme(plot.title = element_text(hjust = 0.5))
  return (AA)
}




