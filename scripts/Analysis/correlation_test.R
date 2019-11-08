#install.packages(c("dplyr","scales","relaimpo","rms","e1071","Hmisc"))
#install.packages("rms")
#install.packages("mvtnorm")
library(dplyr)
library(scales)
require(relaimpo)
library(rms)
library(e1071)
library(Hmisc)

###########################################
#
# BUG LEVEL CORRELATION TEST
#
###########################################

#Read in CSV
bug_data <- read.csv("/home/kjbaron/Documents/NABATS/intermediate_files/target_bfcs.csv", header = TRUE)

#bug_data <- filter(bug_data, project == "CXF")

boxplot(author_exp~priority,data=bug_data, main="Correlation between Priority and Exp",
        xlab="Priority", ylab="Experience")

# -1 indicates a strong negative correlation : this means that every time x increases, y decreases (left panel figure)
#  0 means that there is no association between the two variables (x and y) (middle panel figure)
#  1 indicates a strong positive correlation : this means that y increases with x (right panel figure)

res <- cor.test(bug_data$priority, bug_data$author_exp, method = "pearson")
res$p.value
res$estimate






###########################################
#
# FILE LEVEL CORRELATION TEST
#
###########################################






#Read in CSV
file_data <- read.csv("/home/kjbaron/Documents/NABATS/intermediate_files/final_dataset.csv", header = TRUE)
file_data <- filter(file_data, priority > 0)


#Since bfs, priority, and exp are all sumations, I calculate the averages before calculating the correlation
file_data$avg_exp <- with(file_data, ifelse(num_bugs==0, 0, exp/num_bugs))
file_data$avg_pri <- with(file_data, ifelse(num_bugs==0, 0, priority/num_bugs))



library("ggpubr")
ggscatter(file_data, x = "avg_pri", y = "avg_exp", 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Priority", ylab = "Experience")


# -1 indicates a strong negative correlation : this means that every time x increases, y decreases (left panel figure)
#  0 means that there is no association between the two variables (x and y) (middle panel figure)
#  1 indicates a strong positive correlation : this means that y increases with x (right panel figure)

res <- cor.test(file_data$priority, file_data$exp, method = "pearson")
res
res$p.value
res$estimate
























