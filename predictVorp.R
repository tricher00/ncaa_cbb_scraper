setwd("C://Users/richert/git/ncaa_cbb_scraper")
data <- read.csv("collegeStatsAndVorp.csv")
data <- data[,-1]
dataNorm <- scale(data[,3:9])
data[,3:9] <- dataNorm
pca <- prcomp(data[,3:9],scale=T)
pc1 <- pca$rotation[,1]
pc2 <- pca$rotation[,2]

lm(data$VORP ~ data$PPG + data$RPG + data$SPG + data$BPG + data$ASTO + data$TS + data$SOS)

dfs <- list()
acc1 <- numeric()
acc3 <- numeric()
acc5 <- numeric()
dists <- numeric()
j <- 1
for (year in 2012:2017){
  df <- data.frame()
  num1 <- 0
  num3 <- 0
  num5 <- 0
  
  train <- data[data$Year != year,]
  test <- data[data$Year == year,]
  
  model <- lm(train$VORP ~ train$PPG + train$RPG + train$SPG + train$BPG + train$ASTO + train$TS + train$SOS)
  
  b <- as.numeric(model$coefficients[1])
  co1 <- as.numeric(model$coefficients[2])
  co2 <- as.numeric(model$coefficients[3])
  co3 <- as.numeric(model$coefficients[4])
  co4 <- as.numeric(model$coefficients[5])
  co5 <- as.numeric(model$coefficients[6])
  co6 <- as.numeric(model$coefficients[7])
  co7 <- as.numeric(model$coefficients[8])
  
  n <- nrow(test)
  dist <- numeric()
  predicts <- numeric()
  
  for (i in 1:n){
    player <- test[i,]
    y <- co1 * player$PPG + co2 * player$RPG + co3 * player$SPG + co4 * player$BPG + co5 * player$ASTO + co6 * player$TS + co7 * player$SOS + b
    dist[i] <- abs(player$VORP - y)
    predicts[i] <- y
    if (dist[i] <= .5){
      num5 <- num5 + 1
      if (dist[i] <= .3){
        num3 <- num3 + 1
        if (dist[i] <= .1){
          num1 <- num1 + 1
        }
      }
    }
    
  }
  dfs[[j]] <- data.frame(Player = test$Player, VORP = test$VORP, Predict = predicts)
  acc1[j] <- num1/n
  acc3[j] <- num3/n
  acc5[j] <- num5/n
  j <- j + 1
  print(mean(dist))
}

avgAcc1 <- mean(acc1)
avgAcc3 <- mean(acc3)
avgAcc5 <- mean(acc5)

allPredicts <- rbind(dfs[[1]],dfs[[2]],dfs[[3]],dfs[[4]],dfs[[5]],dfs[[6]])
with(allPredicts,plot(VORP, Predict))
r2 <-summary(lm(allPredicts$VORP~allPredicts$Predict))$r.squared

cbb2018 <- read.csv("college2018.csv")
cbb2018 <- cbb2018[cbb2018$Games >= 15,]
cbb2018 <- cbb2018[,-1]
eq <- lm(data$VORP ~ data$PPG + data$RPG + data$SPG + data$BPG + data$ASTO + data$TS + data$SOS)
View(cbb2018)
b <- as.numeric(eq$coefficients[1])
co1 <- as.numeric(eq$coefficients[2])
co2 <- as.numeric(eq$coefficients[3])
co3 <- as.numeric(eq$coefficients[4])
co4 <- as.numeric(eq$coefficients[5])
co5 <- as.numeric(eq$coefficients[6])
co6 <- as.numeric(eq$coefficients[7])
co7 <- as.numeric(eq$coefficients[8])

predict2018 <- numeric()

for (i in 1:nrow(cbb2018)){
  player <- cbb2018[i,]
  asto = player$Asists/(player$TPG*player$Games)
  y <- co1 * player$PPG + co2 * player$RPG + co3 * player$SPG + co4 * player$BPG + co5 * asto + co6 * player$TS + co7 * player$SOS + b
  predict2018[i] <- y
}
df2018 <- data.frame(Player = cbb2018$Player, Predict = predict2018)
