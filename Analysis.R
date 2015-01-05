library(car)
library(ggplot2)

#get the data
colclass <- c('character', 'character', 'character')
colclass <- c(colclass, rep('numeric', 17), 'character','numeric','character')
colnames <- c('Player','Team','Opp','Patt','Pcmp', 'Pyds', 'Ptd','Pint', 'P2p', 'Ruatt', 'Ruyds',
              'Rutd','Ru2pt','Rrec','Ryds','Rtd','R2pt','fum','fumtd','pts','Home','week',
              'Posit')
fanstats <- read.csv('fantasy2014.csv', header = FALSE,
                     colClasses = colclass, nrows = 4000,
                     col.names = colnames)

colclass <- c('numeric','character','character', 'numeric', 'character')
colnames <- c('x','Ofweek', 'Strst','week', 'Player')
startsit <- read.csv('startsit.csv', header = FALSE,
                     colClasses = colclass, nrows = 700,
                     col.names = colnames)

#wrangletime

fullset <- merge(fanstats,startsit, all.x = TRUE)
plyrs <- fullset$Player %in% startsit$Player
fullset <- fullset[plyrs,]
fullset <- fullset[fullset$week >= 6,]


#calc exact fantasy points

expts <- fullset$Pyds/25 + fullset$Ptd*6 - fullset$Pint*2 + fullset$P2p*2 +
          fullset$Ruyds/10 + fullset$Rutd*6 + fullset$Ru2pt*2 + fullset$Ryds/10 +
          fullset$Rtd*6 + fullset$R2pt*2 - fullset$fum*2 + fullset$fumtd*6

exptsppr <- fullset$Pyds/25 + fullset$Ptd*6 - fullset$Pint*2 + fullset$P2p*2 +
    fullset$Ruyds/10 + fullset$Rutd*6 + fullset$Ru2pt*2 + fullset$Ryds/10 +
    fullset$Rtd*6 + fullset$R2pt*2 - fullset$fum*2 + fullset$fumtd*6 + fullset$Rrec

fullset <- data.frame(fullset, expts, exptsppr)
fullset$Strst <- recode(fullset$Strst, "NA = 'Not Selected'")
fullset$Ofweek <- recode(fullset$Ofweek, "NA = 'Not Selected'; 'o' = 'OfWeek'; 'n' = 'NotOfWeek'")


#clean up a bit
remove(colclass, colnames, expts, fanstats, startsit, plyrs)

#between subjects analysis

#standard error for error bars
stan <- function(x) {sd(x)/sqrt(length(x))}

#average points by position
x <- aggregate(expts ~ Posit + Strst, fullset, mean)
xstan <- aggregate(expts ~ Posit + Strst, fullset, stan)
x <- data.frame(x, xstan)

t <- ggplot(x, aes(y = expts, x = Posit, fill = Strst)) +
    geom_bar(stat = 'identity', position = 'dodge', color = 'black') +
    geom_errorbar(aes(ymin = expts - expts.1, ymax = expts + expts.1), #mean of y axis variable +/- se 
                  position = position_dodge(0.9), width = .25) +
    scale_fill_discrete(name = "Start/Sit") +
    xlab("Position") +
    ylab("Avg Fantasy Points") +
    theme(axis.title.x = element_text(size = 15, face = 'bold'), #just some asthetic stuff
          axis.title.y = element_text(size = 15, face = 'bold'), 
          legend.title = element_text(size = 15, face = 'bold'),
          axis.text.x = element_text(angle = 30, hjust = 1, vjust = 1, size = 15, face = 'bold'),
          axis.text.y = element_text(size = 15))

print(t)

remove(x, xstan)

###get average by position per week and then plot it
x <- aggregate(expts ~ Strst + week + Posit, fullset, mean)
y <- aggregate(expts ~ Strst + week + Posit, fullset, stan)
x <- data.frame(x,y)

t <- ggplot(x, aes(x = week, y = expts, z = Posit, col = Strst)) +
    geom_line() +
    geom_point() +
    geom_errorbar(aes(ymin = expts - expts.1, ymax = expts + expts.1), width = .10) +
    scale_x_continuous(breaks = 6:15) +
    scale_color_discrete(name = "Start/Sit") +
    facet_grid(Posit ~ .) +
    xlab("Week") +
    ylab("Avg Fantasy Points") +
    theme(axis.title.x = element_text(size = 15, face = 'bold'), #just some asthetic stuff
          axis.title.y = element_text(size = 15, face = 'bold'), 
          legend.title = element_text(size = 15, face = 'bold'),
          axis.text.x = element_text(size = 15, face = 'bold'),
          axis.text.y = element_text(size = 15))

print(t)

remove(x, xstan, y)

###time to count### first do some calculation of deviation scores
wkly <- aggregate(expts ~ Posit + week, fullset, mean)
names(wkly)[3] <- "Avg"
fullset <- merge(fullset, wkly)
dv <- fullset$expts - fullset$Avg
fullset <-data.frame(fullset,dv)

#add it to the dataframe
fullset <- data.frame(fullset, dv)

remove(dv,dvs,i,t)

#write a function that counts positive deviations
#a positive deviation means a player was above the mean for
#the week
cnt <- function(x) {
    count = 0
    tot = 0
    for (i in x){
        if (i == abs(i)){
            count = count + 1
        }
        tot = tot + 1
    }
    count/tot
}
#Average percent of players above the mean by position
stavg <- tapply(fullset$dv, fullset$Strst, cnt)
dvavg <- cnt(fullset$dv)
exptavg <- tapply(fullset$expts, fullset$Strst, mean)

x <- aggregate(dv ~ Posit + Strst, fullset, cnt)

t <- ggplot(x, aes(y = dv, x = Posit, fill = Strst)) +
    geom_bar(stat = 'identity', position = 'dodge', color = 'black') +
    xlab("Position") +
    scale_fill_discrete(name="Start/Sit") +
    ylab("% of Players Above Position Average") +
    theme(axis.title.x = element_text(size = 15, face = 'bold'), #just some asthetic stuff
          axis.title.y = element_text(size = 15, face = 'bold'), 
          legend.title = element_text(size = 15, face = 'bold'),
          axis.text.x = element_text(angle= 30, hjust = 1, vjust = 1, size = 15, face = 'bold'),
          axis.text.y = element_text(size = 15))

print(t)

remove(x)

##now do the previous with position as well
x <- aggregate(dv ~ week + Strst + Posit, fullset, cnt)
x <- x[x$week >= 6,]

t <- ggplot(x, aes(x = week, y = dv, z = Posit, col = Strst)) +
    geom_line() +
    geom_point(size = 1.5) +
    scale_color_discrete(name = "Start/Sit") +
    scale_x_continuous(breaks = 6:15) +
    facet_grid(Posit ~ .) +
    xlab("Week") +
    ylab("% of Players Above Position Average") +
    theme(axis.title.x = element_text(size = 15, face = 'bold'), #just some asthetic stuff
          axis.title.y = element_text(size = 15, face = 'bold'), 
          legend.title = element_text(size = 15, face = 'bold'),
          axis.text.x = element_text(size = 15, face = 'bold'),
          axis.text.y = element_text(size = 15))

print(t)

remove(x)

###a random count function for later

cntot <- function (x){ #need to count the number of times he judged each player 
    count <- 0
    for (i in x){
        count <- count+1
        
    }
    count
}

#Now do the same analysis for the "of the week" group....errrg too much munging
#urge to be lazy rising...

x <- aggregate(expts ~ Posit + Strst + Ofweek, fullset, mean)
xstan <- aggregate(expts ~ Posit + Strst + Ofweek, fullset, stan)
x <-data.frame(x,xstan)
x <- x[x$Ofweek != 'Not Selected',]


t <- ggplot(x, aes(x = Posit, y = expts, z = Strst, fill = Ofweek)) +
    geom_bar(stat = "identity", position = "dodge", color = "black") +
    geom_errorbar(aes(ymin = expts - expts.1, ymax = expts + expts.1), #mean of y axis variable +/- se 
                  position = position_dodge(0.9), width = .25) +
    facet_grid(Strst ~ .) +
    xlab("Position") +
    ylab("Average Fantasy Points") +
    theme(axis.title.x = element_text(size = 15, face = 'bold'), #just some asthetic stuff
          axis.title.y = element_text(size = 15, face = 'bold'), 
          legend.title = element_text(size = 15, face = 'bold'),
          axis.text.x = element_text(angle = 30, hjust = 1, vjust = 1, size = 15, face = 'bold'),
          axis.text.y = element_text(size = 15))

print(t)

remove(x, xstan)

##Any players he was good with?
x <- aggregate(expts ~ Player + Strst, fullset, mean)
x <- x[x$Strst == 'Start',]
y <- aggregate(Avg ~ Player + Strst, fullset, mean)
y <- y[y$Strst == 'Start',]
z <- aggregate(expts ~ Player + Strst, fullset, cntot)
z <- z[z$Strst == 'Start',]
q <- aggregate(expts ~ Player + Strst, fullset, stan)
q <- q[q$Strst == 'Start',]
w <- aggregate(expts ~ Player + Strst, fullset, cnt)
w <- w[w$Strst == 'Start',]

x <- merge(x, y, all.x = TRUE)
x <- merge(x, w, all.x = TRUE, by.x = "Player", by.y = "Player")
x <- x[,c(1,3,4,6)]
names(x)[c(2,4)] <- c("Points","Percent")
x <- merge(x, z, all.x = TRUE, by.x = "Player", by.y = "Player")
x <- merge(x, q, all.x = TRUE, by.x = "Player", by.y = "Player")
x <- x[,c(-5,-7)]
names(x)[5:6] <- c("Count", "SE")
x<- x[x$Count >= 3,]

remove(q,x,y,z,w)

#figure out how much more variance is explained by his start sit judgements

lm0 <- lm(expts ~ 1, data = fullset)
lm1 <- lm(expts ~ Strst, data = fullset)
lm2 <- lm(expts ~ Strst + Posit + Posit*Strst, data = fullset)
