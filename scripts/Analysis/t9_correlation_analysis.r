
#install.packages(c("dplyr","scales","relaimpo","rms","e1071","Hmisc"))
#install.packages("rms")
#install.packages("mvtnorm")

library(dplyr)
library(scales)
require(relaimpo)
library(rms)
library(e1071)
library(Hmisc)

#Read in CSV
df <- read.csv("/home/kjbaron/Documents/NABATS/intermediate_files/final_dataset.csv", header = TRUE)
df <- filter(df, num_bugs > 0)

#Since bfs, priority, and exp are all sumations, I calculate the averages before calculating the correlation
df$avg_bfs <- with(df, ifelse(num_bugs==0, 0, bfs/num_bugs))
df$avg_exp <- with(df, ifelse(num_bugs==0, 0, exp/num_bugs))
df$avg_pri <- with(df, ifelse(num_bugs==0, 0, priority/num_bugs))

#Create a df
t9_results <- matrix(ncol=10, nrow=13)
t9_results[1,] <- c("Project", "Y bfs","","","exp","","","priority","","")
t9_results[2,] <- c("","R1","R2","R3","R1","R2","R3","R1","R2","R3")
i <- 3

num_iter = 1000
#RMS package requires a data distribution when building a model
for (current_project in c("accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"))
{
  
  #Extract project
  p_df <- filter(df, project == current_project)
  
  #Add project name to row
  t9_results[i,1] <- current_project
  
  releases <- unique(p_df[c("minor")])
  j<-1
  for (r in releases[["minor"]]){
    
    r_df <- filter(p_df, minor == r)
    #r_df[c("avg_exp","avg_bfs","num_bugs","avg_pri")] <- lapply(r_df[c("avg_exp","avg_bfs","num_bugs","avg_pri")], function(x) c(scale(x, center= min(x), scale=diff(range(x)))))
    
    bfs_corr <- cor.test(r_df$avg_bfs, r_df$num_bugs,method = "pearson")$estimate
    exp_corr <- cor.test(r_df$avg_exp, r_df$num_bugs,method = "pearson")$estimate
    pri_corr <- cor.test(r_df$avg_pri, r_df$num_bugs,method = "pearson")$estimate
    
    library("ggpubr")
    print(current_project)
    ggscatter(r_df, x = "avg_pri", y = "num_bugs", 
              add = "reg.line", conf.int = TRUE, 
              cor.coef = TRUE, cor.method = "pearson",
              xlab = "Priority", ylab = "num_bugs") %>% ggexport(filename = paste("t9_plots/",current_project,r,".png"))
    
    
    t9_results[i,1+j] <- bfs_corr
    t9_results[i,4+j] <- exp_corr
    t9_results[i,7+j] <- pri_corr
    
    j<-j+1
    
  }
  i <- i+1
}


write.csv(t9_results, file = "/home/kjbaron/Documents/NABATS/intermediate_files/t9.csv",row.names=FALSE,na="")

