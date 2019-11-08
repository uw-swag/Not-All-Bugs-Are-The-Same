
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
df <- read.csv("/home/kjbaron/Documents/NABATS/intermediate_files/final_dataset2.csv", header = TRUE)
#df <- filter(df, num_bugs > 0)
#df <- na.omit(df) #remove rows with na values

#df <- filter(df, num_post > 0)

################################################################################
# (MC-1) Estimate budget for degrees of freedom
################################################################################
#Since we plan to fit using ordinary least squares, we use the below rule of
# thumb to estimate our budget
print( floor(min(nrow(df[df$exp > 0,]), nrow(df[df$exp == 0,]) )/15))
print(floor(min(nrow(df[df$bfs > 0,]), nrow(df[df$bfs == 0,]) )/15))
print(floor(min(nrow(df[df$num_bugs > 0,]), nrow(df[df$num_bugs == 0,]) )/15))

################################################################################
# (MC -2) Normality adjustment
################################################################################
# Normalize indep. & dep. variables with min-max
df[c("LOC","CC","churn","exp","bfs","num_bugs","priority")] <- lapply(df[c("LOC","CC","churn","exp","bfs","num_bugs","priority")], function(x) c(scale(x, center= min(x), scale=diff(range(x))))) 

#Set independent variable names
ind_vars = c("LOC","CC","churn")

################################################################################
# (MC -3) Correlation analysis
################################################################################
#Calculate spearman's correlation between independent variables
vc <- varclus(~ ., data=df[,ind_vars], trans="abs")

#Plot hierarchical clusters and the spearman's correlation threshold of 0.7
plot(vc)
threshold <- 0.7
abline(h=1-threshold, col = "red", lty = 2)

################################################################################
# (MC -4) Redundancy analysis
################################################################################
red <- redun(~ ., data=df[,ind_vars], nk=0)
print(red)

sp <- spearman2(formula(paste("num_bugs" ," ~ ",paste0(ind_vars, collapse=" + "))), data= df, p=2)
plot(sp)
print(sp)


################################################################################
# (MC -5) Fit regression model
################################################################################
#Create a matrix to fill with R^2 values
r2_results <- matrix(ncol=5, nrow=12)
r2_results[1,] <- c("Project", "Y #Bugs", "Y ChgLines", "Y Exp", "Y Priority")
i <- 2

num_iter = 1000
#RMS package requires a data distribution when building a model
for (current_project in c("accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"))
{
  print(current_project)
  
  #Extract project
  p_df <- filter(df, project == current_project)
  p_df[c("LOC","CC","churn","exp","bfs","num_bugs","priority")] <- lapply(p_df[c("LOC","CC","churn","exp","bfs","num_bugs","priority")], function(x) c(scale(x, center= min(x), scale=diff(range(x))))) 
  

  #RMS package requires a data distribution when building a model
  print(dim(p_df[,c("exp",ind_vars)]))
  dd_exp <- datadist(p_df[,c("exp",ind_vars)])
  options(datadist = "dd_exp")
  
  dd_bfs <- datadist(p_df[,c("bfs",ind_vars)])
  options(datadist = "dd_bfs")
  
  dd_bugs <- datadist(p_df[,c("num_bugs",ind_vars)])
  options(datadist = "dd_bugs")
  
  dd_priority <- datadist(p_df[,c("priority",ind_vars)])
  options(datadist = "dd_priority")

  #Build generalized linear models for each dependent variable
  fit_exp <- lm(exp ~ LOC+CC+churn, data=p_df, x=T, y=T)
  #print(summary(fit_exp))
  fit_bfs <- lm(bfs ~ LOC+CC+churn, data=p_df, x=T, y=T)
  #print(summary(fit_bfs))
  fit_bugs <- lm(num_bugs ~ LOC+CC+churn, data=p_df, x=T, y=T)
  #print(summary(fit_bugs))
  fit_priority <- lm(priority ~ LOC+CC+churn, data=p_df, x=T, y=T)
  
  #Calculate R^2
  #lmg is the R^2 contribution averaged over orderings among regressors\
  # Metrics normalized to sum to 100% --> (rela=TRUE), otherwise --> (rela=FALSE)
  r2_exp <- calc.relimp(fit_exp, type="lmg", rela=FALSE)@R2
  r2_bfs <- calc.relimp(fit_bfs, type="lmg", rela=FALSE)@R2
  r2_bugs <- calc.relimp(fit_bugs, type="lmg", rela=FALSE)@R2
  r2_priority <- calc.relimp(fit_priority, type="lmg", rela=FALSE)@R2
  print(1)
  #Add results to maxtrix
  r2_results[i,] <- c(current_project, r2_bugs, r2_bfs, r2_exp, r2_priority)
  i <- i+1
}


write.csv(r2_results, file = "/home/kjbaron/Documents/NABATS/intermediate_files/r2_results.csv",row.names=FALSE,na="")


#  The code below is most the same as for Table 5, but rela=TRUE in the relimp calculation 
#  -- just separated the code by table to keep it easy to read
#  --------------------------------------------------------------------------------------------------------------------------
#  TABLE 6 - Average contributions from each independent variable when different dependent variables are used
#  --------------------------------------------------------------------------------------------------------------------------


#Create a matrix to fill with values
t6_results <- matrix(ncol=6, nrow=34)
t6_results[1,] <- c("Project", "Features", "Y #Bugs", "Y ChgLines", "Y Exp", "Y Priority")
i <- 2

#Calculate contributions for each dependent variable of each project
for (current_project in c("accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"))
{
  
  print(current_project)
  
  #Extract project data and standardize indep. & dep. variables
  p_df <- filter(df, project == current_project)
  p_df[c("LOC","CC","churn","exp","bfs","num_bugs","priority")] <- lapply(p_df[c("LOC","CC","churn","exp","bfs","num_bugs","priority")], function(x) c(scale(x, center= min(x), scale=diff(range(x))))) 
  
  
  
  #Build generalized linear models for each dependent variable
  m_exp <- lm(exp ~ LOC+CC+churn, data=p_df, x=T, y=T)
  #print(summary(fit_exp))
  m_bfs <- lm(bfs ~ LOC+CC+churn, data=p_df, x=T, y=T)
  #print(summary(fit_bfs))
  m_bugs <- lm(num_bugs ~ LOC+CC+churn, data=p_df, x=T, y=T)
  #print(summary(m_bugs))
  m_priority <- lm(priority ~ LOC+CC+churn, data=p_df, x=T, y=T)
  
  ## RCS WAS CAUSING ERROR, FIND OUT WHY
  
  print(1)
  #Build generalized linear models for each dependent variable
  #m_exp <- lm(exp ~ LOC+CC+rcs(churn,3), data=p_df, x=T, y=T)
  #m_bfs <- lm(bfs ~  LOC+CC+rcs(churn,3), data=p_df, x=T, y=T)
  #m_bugs <- lm(num_bugs ~ LOC+CC+rcs(churn,3), data=p_df, x=T, y=T)
  
  print(2)
  #Calculate R^2
  #lmg is the R^2 contribution averaged over orderings among regressors
  lmg_exp <- calc.relimp(m_exp, type="lmg", rela=TRUE)@lmg
  lmg_bfs <- calc.relimp(m_bfs, type="lmg", rela=TRUE)@lmg
  lmg_bugs <- calc.relimp(m_bugs, type="lmg", rela=TRUE)@lmg
  lmg_priority <- calc.relimp(m_priority, type="lmg", rela=TRUE)@lmg

  
  print(3)
  #Add results to maxtrix
  t6_results[i,] <- c(current_project, "X LOC", lmg_bugs['LOC'], lmg_bfs['LOC'], lmg_exp['LOC'], lmg_priority['LOC'])
  t6_results[i+1,] <- c(current_project, "X CC", lmg_bugs['CC'], lmg_bfs['CC'], lmg_exp['CC'], lmg_priority['CC'])
  t6_results[i+2,] <- c(current_project, "X churn", lmg_bugs['churn'], lmg_bfs['churn'], lmg_exp['churn'], lmg_priority['churn'])
  
  ## RCS ERROR DOWN HERE TOO!!! AHHHHHH
  
  #t6_results[i+2,] <- c(current_project, "X churn", lmg_bugs['rcs(churn, 3).churn'], lmg_bfs['rcs(churn, 3).churn'], lmg_exp['rcs(churn, 3).churn'])
  i <- i+3
}

write.csv(t6_results, file = "/home/kjbaron/Documents/NABATS/intermediate_files/t6_results.csv",row.names=FALSE,na="")
