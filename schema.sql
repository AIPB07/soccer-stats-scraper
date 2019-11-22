CREATE TABLE `goals` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerName` varchar(45) NOT NULL,
  `Opponent` varchar(24) NOT NULL,
  `Time` int(11) NOT NULL,
  `Home_Away` char(4) NOT NULL,
  `Gameweek` int(11) NOT NULL,
  `Assist` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `player_mins` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerName` varchar(45) NOT NULL,
  `Minutes` int(11) NOT NULL,
  `Seconds` int(11) NOT NULL,
  `Gameweek` int(11) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1188 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `player_teams` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerName` varchar(45) NOT NULL,
  `TeamName` varchar(24) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=411 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `results` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `HomeTeam` varchar(24) NOT NULL,
  `HomeGoals` int(11) NOT NULL,
  `AwayTeam` varchar(24) NOT NULL,
  `AwayGoals` int(11) NOT NULL,
  `FixtureURL` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;