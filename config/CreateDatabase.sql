CREATE TABLE `Roles` (
  `RoleID` int(10) unsigned NOT NULL auto_increment,
  `Name` varchar(50) NOT NULL default '',
  PRIMARY KEY  (`RoleID`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Users` (
  `UserID` int(10) unsigned NOT NULL auto_increment,
  `Username` varchar(40) NOT NULL default '',
  `Password` varchar(60) NOT NULL default '',
  `RoleID` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`UserID`),
  UNIQUE KEY `Username` (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO Roles VALUES (0, "Administrator");
