/* Create the database tables */

DROP TABLE IF EXISTS Users;
CREATE TABLE Users
(
    UserID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    Username VARCHAR(30) NOT NULL,
    Password VARCHAR(30) NOT NULL,
    FirstName VARCHAR(20) NOT NULL,
    LastName VARCHAR(20) NOT NULL,
    RoleID INT UNSIGNED NOT NULL,
    ClientState VARCHAR(2048) NOT NULL,
    PRIMARY KEY (UserID),
    UNIQUE KEY (Username)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS Roles;
CREATE TABLE Roles
(
    RoleID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    RoleName VARCHAR(30) NOT NULL,
    Flags int unsigned NOT NULL,
    PRIMARY KEY (RoleID),
    UNIQUE KEY (RoleName)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS Sequences;
CREATE TABLE Sequences
(
    SequenceID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    Name VARCHAR(64) NOT NULL,
    Comment VARCHAR(255),
    Type VARCHAR(20),
    CreationDate TIMESTAMP DEFAULT NOW(),
    UserID INT UNSIGNED NOT NULL,
    FirstComponentID INT UNSIGNED NOT NULL,
    ComponentCount INT UNSIGNED NOT NULL,
    Valid BOOL NOT NULL,
    Dirty BOOL NOT NULL,
    PRIMARY KEY (SequenceID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS Reagents;
CREATE TABLE Reagents
(
    ReagentID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    SequenceID INT UNSIGNED NOT NULL,
    ComponentID INT UNSIGNED NOT NULL,
    Position VARCHAR(2) NOT NULL,
    Available BOOL NOT NULL,
    Name VARCHAR(64) NOT NULL,
    Description VARCHAR(255) NOT NULL,
    PRIMARY KEY (ReagentID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS Components;
CREATE TABLE Components
(
    ComponentID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    SequenceID INT UNSIGNED NOT NULL,
    PreviousComponentID INT UNSIGNED NOT NULL,
    NextComponentID INT UNSIGNED NOT NULL,
    Type VARCHAR(20) NOT NULL,
    Name VARCHAR(64),
    Details VARCHAR(2048) NOT NULL,
    PRIMARY KEY (ComponentID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS SystemLog;
CREATE TABLE SystemLog
(
    LogID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    Date TIMESTAMP DEFAULT NOW(),
    Level INT UNSIGNED NOT NULL,
    UserID INT UNSIGNED NOT NULL,
    Message VARCHAR(1024) NOT NULL,
    PRIMARY KEY (LogID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS RunLog;
CREATE TABLE RunLog
(
    LogID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    Date TIMESTAMP DEFAULT NOW(),
    Level INT UNSIGNED NOT NULL,
    UserID INT UNSIGNED NOT NULL,
    SequenceID INT UNSIGNED NOT NULL,
    ComponentID INT UNSIGNED,
    Message VARCHAR(1024) NOT NULL,
    PRIMARY KEY (LogID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS StatusLog;
CREATE TABLE StatusLog
(
    LogID INT UNSIGNED NOT NULL AUTO_INCREMENT,
    Date TIMESTAMP DEFAULT NOW(),
    VacuumSystemOn BOOL,
    VacuumSystemPressure FLOAT,
    CoolingSystemOn BOOL,
    PressureRegulator1SetPressure FLOAT,
    PressureRegulator1ActualPressure FLOAT,
    PressureRegulator2SetPressure FLOAT,
    PressureRegulator2ActualPressure FLOAT,
    GasTransferValveOpen BOOL,
    F18LoadValveOpen BOOL,
    HPLCLoadValveOpen BOOL,
    ReagentRobotPositionSet VARCHAR(64),
    ReagentRobotPositionActual VARCHAR(64),
    ReagentRobotPositionSetX INT,
    ReagentRobotPositionSetY INT,
    ReagentRobotPositionActualX INT,
    ReagentRobotPositionActualY INT,
    ReagentRobotStatusX VARCHAR(64),
    ReagentRobotStatusY VARCHAR(64),
    ReagentRobotControlX INT UNSIGNED,
    ReagentRobotControlY INT UNSIGNED,
    ReagentRobotCheckX INT UNSIGNED,
    ReagentRobotCheckY INT UNSIGNED,
    GripperSetUp BOOL,
    GripperSetDown BOOL,
    GripperSetOpen BOOL,
    GripperSetClose BOOL,
    GasTransferSetUp BOOL,
    GasTransferSetDown BOOL,
    GripperUp BOOL,
    GripperDown BOOL,
    GripperOpen BOOL,
    GripperClose BOOL,
    GasTransferUp BOOL,
    GasTransferDown BOOL,
    Reactor1SetPosition VARCHAR(30),
    Reactor1ActualPosition VARCHAR(30),
    Reactor1SetY INT,
    Reactor1ActualY INT,
    Reactor1RobotStatus VARCHAR(30),
    Reactor1RobotControl INT UNSIGNED,
    Reactor1RobotCheck INT UNSIGNED,
    Reactor1SetUp BOOL,
    Reactor1SetDown BOOL,
    Reactor1Up BOOL,
    Reactor1Down BOOL,
    Reactor1Stopcock1Position VARCHAR(4),
    Reactor1Stopcock2Position VARCHAR(4),
    Reactor1Stopcock3Position VARCHAR(4),
    Reactor1Collet1On BOOL,
    Reactor1Collet1SetTemperature FLOAT,
    Reactor1Collet1ActualTemperature FLOAT,
    Reactor1Collet2On BOOL,
    Reactor1Collet2SetTemperature FLOAT,
    Reactor1Collet2ActualTemperature FLOAT,
    Reactor1Collet3On BOOL,
    Reactor1Collet3SetTemperature FLOAT,
    Reactor1Collet3ActualTemperature FLOAT,
    Reactor1StirMotor INT UNSIGNED,
    Reactor1RaditationDetector FLOAT,
    Reactor2SetPosition VARCHAR(30),
    Reactor2ActualPosition VARCHAR(30),
    Reactor2SetY INT,
    Reactor2ActualY INT,
    Reactor2RobotStatus VARCHAR(30),
    Reactor2RobotControl INT UNSIGNED,
    Reactor2RobotCheck INT UNSIGNED,
    Reactor2SetUp BOOL,
    Reactor2SetDown BOOL,
    Reactor2Up BOOL,
    Reactor2Down BOOL,
    Reactor2Stopcock1Position VARCHAR(4),
    Reactor2Collet1On BOOL,
    Reactor2Collet1SetTemperature FLOAT,
    Reactor2Collet1ActualTemperature FLOAT,
    Reactor2Collet2On BOOL,
    Reactor2Collet2SetTemperature FLOAT,
    Reactor2Collet2ActualTemperature FLOAT,
    Reactor2Collet3On BOOL,
    Reactor2Collet3SetTemperature FLOAT,
    Reactor2Collet3ActualTemperature FLOAT,
    Reactor2StirMotor INT UNSIGNED,
    Reactor2RaditationDetector FLOAT,
    Reactor3SetPosition VARCHAR(30),
    Reactor3ActualPosition VARCHAR(30),
    Reactor3SetY INT,
    Reactor3ActualY INT,
    Reactor3RobotStatus VARCHAR(30),
    Reactor3RobotControl INT UNSIGNED,
    Reactor3RobotCheck INT UNSIGNED,
    Reactor3SetUp BOOL,
    Reactor3SetDown BOOL,
    Reactor3Up BOOL,
    Reactor3Down BOOL,
    Reactor3Stopcock1Position VARCHAR(4),
    Reactor3Collet1On BOOL,
    Reactor3Collet1SetTemperature FLOAT,
    Reactor3Collet1ActualTemperature FLOAT,
    Reactor3Collet2On BOOL,
    Reactor3Collet2SetTemperature FLOAT,
    Reactor3Collet2ActualTemperature FLOAT,
    Reactor3Collet3On BOOL,
    Reactor3Collet3SetTemperature FLOAT,
    Reactor3Collet3ActualTemperature FLOAT,
    Reactor3StirMotor INT UNSIGNED,
    Reactor3RaditationDetector FLOAT,
    PRIMARY KEY (LogID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

