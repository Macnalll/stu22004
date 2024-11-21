# v2 changes:
# made simulation occur 1000 times and only shows the winners and their probability

# load files
plStats <- read.csv("PL stats after 10th nov.csv", row.names = 1)
finalStats <- plStats
finalStats$Shots <- NULL
plRemaining <- read.csv("PL results after 10th nov (Matchday 11).csv", row.names = 1, stringsAsFactors = FALSE)

# find more stats
plStats$goalChance <- plStats$GF / plStats$Shots
plStats$xGoalsPerGame <- plStats$GF / (plStats$Wins + plStats$Draws + plStats$Losses)
plStats$xConcededPerGame <- plStats$GA / (plStats$Wins + plStats$Draws + plStats$Losses)
plStats$xShotsPerGame <- plStats$Shots / (plStats$Wins + plStats$Draws + plStats$Losses)

# convert empty cells to NA and create new data frame with all remaining matches
plRemaining[plRemaining == ""] <- NA
naValues <- which(is.na(plRemaining), arr.ind = TRUE)
remainingMatches <- data.frame(
  home = rownames(plRemaining)[naValues[, 1]],
  away = colnames(plRemaining)[naValues[, 2]]
)

# simulate a single match
match <- function(home, away, plStats, finalStats) {
  lambdaHome <- lambda(home, plStats)
  lambdaAway <- lambda(away, plStats)
  homeGoal <- rpois(1, lambdaHome)
  awayGoal <- rpois(1, lambdaAway)
  if (homeGoal > awayGoal) {
    return(c(home, away, homeGoal, awayGoal, 3, 0))
  }
  else if (homeGoal < awayGoal) {
    return(c(home, away, homeGoal, awayGoal, 0, 3))
  }
  else {
    return(c(home, away, homeGoal, awayGoal, 1, 1))
  }
}

# simple lambda based on expected goals only
lambda <- function(Club, plStats) {
  teamRow <- plStats[rownames(plStats) == Club, ]
  return(teamRow$xGoalsPerGame)
}

# simulate for remaining matches and update finalStats
# for (i in seq_len(nrow(remainingMatches))) {
#   home <- remainingMatches$home[i]
#   away <- remainingMatches$away[i]
#   
#   result <- match(home, away, plStats, finalStats)
#   
#   # get values
#   homeGoals <- as.numeric(result[3])
#   awayGoals <- as.numeric(result[4])
#   homePoints <- as.numeric(result[5])
#   awayPoints <- as.numeric(result[6])
#   
#   finalStats[home, "GF"] <- finalStats[home, "GF"] + homeGoals
#   finalStats[away, "GF"] <- finalStats[away, "GF"] + awayGoals
#   finalStats[home, "GA"] <- finalStats[home, "GA"] + awayGoals
#   finalStats[away, "GA"] <- finalStats[away, "GA"] + homeGoals
#   
#   if (homePoints == 3) {
#     # home
#     finalStats[home, "Points"] <- finalStats[home, "Points"] + 3
#     finalStats[home, "Wins"] <- finalStats[home, "Wins"] + 1
#     finalStats[away, "Losses"] <- finalStats[away, "Losses"] + 1
#   } else if (awayPoints == 3) {
#     # away
#     finalStats[away, "Points"] <- finalStats[away, "Points"] + 3
#     finalStats[away, "Wins"] <- finalStats[away, "Wins"] + 1
#     finalStats[home, "Losses"] <- finalStats[home, "Losses"] + 1
#   } else {
#     # draw
#     finalStats[home, "Points"] <- finalStats[home, "Points"] + 1
#     finalStats[away, "Points"] <- finalStats[away, "Points"] + 1
#     finalStats[home, "Draws"] <- finalStats[home, "Draws"] + 1
#     finalStats[away, "Draws"] <- finalStats[away, "Draws"] + 1
#   }
# }
# 
# finalStats <- finalStats[order(finalStats$Points, decreasing=TRUE),] 

season <- function(plStats, plRemaining, finalStats) {
  remainingMatches <- data.frame(
    home = rownames(plRemaining)[which(is.na(plRemaining), arr.ind = TRUE)[, 1]],
    away = colnames(plRemaining)[which(is.na(plRemaining), arr.ind = TRUE)[, 2]]
  )
  
  for (i in seq_len(nrow(remainingMatches))) {
    home <- remainingMatches$home[i]
    away <- remainingMatches$away[i]
    result <- match(home, away, plStats, finalStats)
    
    homeGoals <- as.numeric(result[3])
    awayGoals <- as.numeric(result[4])
    homePoints <- as.numeric(result[5])
    awayPoints <- as.numeric(result[6])
    
    finalStats[home, "GF"] <- finalStats[home, "GF"] + homeGoals
    finalStats[away, "GF"] <- finalStats[away, "GF"] + awayGoals
    finalStats[home, "GA"] <- finalStats[home, "GA"] + awayGoals
    finalStats[away, "GA"] <- finalStats[away, "GA"] + homeGoals
    
    if (homePoints == 3) {
      finalStats[home, "Points"] <- finalStats[home, "Points"] + 3
      finalStats[home, "Wins"] <- finalStats[home, "Wins"] + 1
      finalStats[away, "Losses"] <- finalStats[away, "Losses"] + 1
    } else if (awayPoints == 3) {
      finalStats[away, "Points"] <- finalStats[away, "Points"] + 3
      finalStats[away, "Wins"] <- finalStats[away, "Wins"] + 1
      finalStats[home, "Losses"] <- finalStats[home, "Losses"] + 1
    } else {
      finalStats[home, "Points"] <- finalStats[home, "Points"] + 1
      finalStats[away, "Points"] <- finalStats[away, "Points"] + 1
      finalStats[home, "Draws"] <- finalStats[home, "Draws"] + 1
      finalStats[away, "Draws"] <- finalStats[away, "Draws"] + 1
    }
  }
  
  finalStats <- finalStats[order(finalStats$Points, decreasing = TRUE),]
  return(rownames(finalStats)[1])
}

set.seed(0)
simCount <- 1000
wins <- rep(NA, simCount)

for (i in 1:simCount) {
  simFinalStats <- finalStats
  wins[i] <- season(plStats, plRemaining, simFinalStats)
}

winCount <- table(wins)
winProb <- prop.table(winCount)

print(winCount)
print(winProb)


