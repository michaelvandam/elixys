/* Create the stored procedures */

-- Change the delimiter for this file
DELIMITER //

/****************************************************************************************************************************************************************
 ** Logging *****************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Logs a message to the SystemLog table:
 *   IN Timestamp - Log message time stamp
 *   IN Level - Log message level
 *   IN Username - Name of the user that generated the log message
 *   IN Message - Log message
 */
DROP PROCEDURE IF EXISTS SystemLog;
CREATE PROCEDURE SystemLog(IN iTimestamp TIMESTAMP, IN iLevel INT UNSIGNED, IN iUsername VARCHAR(30), IN iMessage VARCHAR(1024))
    BEGIN
        DECLARE lUserID INT UNSIGNED;

        -- Look up the user ID
        SET lUserID = (SELECT UserID FROM Users WHERE Username = iUsername);

        -- Insert the entry
        IF lUserID IS NOT NULL THEN
            INSERT INTO SystemLog VALUES (NULL, iTimestamp, iLevel, lUserID, iMessage);
        END IF;
    END //

/* Logs a message to the RunLog table:
 *   IN Timestamp - Log message timestamp
 *   IN Level - Log message level
 *   IN Username - Name of the user that generated the log message
 *   IN SequenceID - ID of the sequence that is currently running
 *   IN ComponentID - ID of the component that is currently running
 *   IN Message - Log message
 */
DROP PROCEDURE IF EXISTS RunLog;
CREATE PROCEDURE RunLog(IN iTimestamp TIMESTAMP, IN iLevel INT UNSIGNED, IN iUsername VARCHAR(30), IN iSequenceID INT UNSIGNED, IN iComponentID INT UNSIGNED, IN iMessage VARCHAR(1024))
    BEGIN
        DECLARE lUserID INT UNSIGNED;

        -- Look up the user ID
        SET lUserID = (SELECT UserID FROM Users WHERE Username = iUsername);

        -- Insert the entry
        IF lUserID IS NOT NULL THEN
            INSERT INTO RunLog VALUES (NULL, iTimestamp, iLevel, lUserID, iSequenceID, iComponentID, iMessage);
        END IF;
    END //

/* Logs a message to the StatusLog table containing the current status of the system. */
DROP PROCEDURE IF EXISTS StatusLog;
CREATE PROCEDURE StatusLog(IN iTimestamp TIMESTAMP, IN iVacuumSystemOn BOOL, IN iVacuumSystemPressure FLOAT, IN iCoolingSystemOn BOOL, IN iPressureRegulator1SetPressure FLOAT,
      IN iPressureRegulator1ActualPressure FLOAT, IN iPressureRegulator2SetPressure FLOAT, IN iPressureRegulator2ActualPressure FLOAT, IN iGasTransferValveOpen BOOL,
      IN iF18LoadValveOpen BOOL, IN iHPLCLoadValveOpen BOOL, IN iReagentRobotPositionSet VARCHAR(64), IN iReagentRobotPositionActual VARCHAR(64), IN iReagentRobotPositionSetX INT,
      IN iReagentRobotPositionSetY INT, IN iReagentRobotPositionActualX INT, IN iReagentRobotPositionActualY INT, IN iReagentRobotStatusX VARCHAR(64),
      IN iReagentRobotStatusY VARCHAR(64), IN iReagentRobotErrorX INT UNSIGNED, IN iReagentRobotErrorY INT UNSIGNED, IN iReagentRobotControlX INT UNSIGNED, 
      IN iReagentRobotControlY INT UNSIGNED, IN iReagentRobotCheckX INT UNSIGNED, IN iReagentRobotCheckY INT UNSIGNED, IN iGripperSetUp BOOL, IN iGripperSetDown BOOL, 
      IN iGripperSetOpen BOOL, IN iGripperSetClose BOOL, IN iGasTransferSetUp BOOL, IN iGasTransferSetDown BOOL, IN iGripperUp BOOL, IN iGripperDown BOOL, IN iGripperOpen BOOL, 
      IN iGripperClose BOOL, IN iGasTransferUp BOOL, IN iGasTransferDown BOOL, IN iReactor1SetPosition VARCHAR(30), IN iReactor1ActualPosition VARCHAR(30), 
      IN iReactor1SetY INT, IN iReactor1ActualY INT, IN iReactor1RobotStatus VARCHAR(30), IN iReactor1RobotError INT UNSIGNED, IN iReactor1RobotControl INT UNSIGNED, 
      IN iReactor1RobotCheck INT UNSIGNED, IN iReactor1SetUp BOOL, IN iReactor1SetDown BOOL, IN iReactor1Up BOOL, IN iReactor1Down BOOL, IN iReactor1Stopcock1Position VARCHAR(4), 
      IN iReactor1Stopcock2Position VARCHAR(4), IN iReactor1Stopcock3Position VARCHAR(4), IN iReactor1Collet1On BOOL, IN iReactor1Collet1SetTemperature FLOAT, 
      IN iReactor1Collet1ActualTemperature FLOAT, IN iReactor1Collet2On BOOL, IN iReactor1Collet2SetTemperature FLOAT, IN iReactor1Collet2ActualTemperature FLOAT, 
      IN iReactor1Collet3On BOOL, IN iReactor1Collet3SetTemperature FLOAT, IN iReactor1Collet3ActualTemperature FLOAT, IN iReactor1StirMotor INT UNSIGNED, 
      IN iReactor1RaditationDetector FLOAT, IN iReactor2SetPosition VARCHAR(30), IN iReactor2ActualPosition VARCHAR(30), IN iReactor2SetY INT, IN iReactor2ActualY INT, 
      IN iReactor2RobotStatus VARCHAR(30), IN iReactor2RobotError INT UNSIGNED, IN iReactor2RobotControl INT UNSIGNED, IN iReactor2RobotCheck INT UNSIGNED, 
      IN iReactor2SetUp BOOL, IN iReactor2SetDown BOOL, IN iReactor2Up BOOL, IN iReactor2Down BOOL, IN iReactor2Stopcock1Position VARCHAR(4), IN iReactor2Collet1On BOOL,
      IN iReactor2Collet1SetTemperature FLOAT, IN iReactor2Collet1ActualTemperature FLOAT, IN iReactor2Collet2On BOOL, IN iReactor2Collet2SetTemperature FLOAT,
      IN iReactor2Collet2ActualTemperature FLOAT, IN iReactor2Collet3On BOOL, IN iReactor2Collet3SetTemperature FLOAT, IN iReactor2Collet3ActualTemperature FLOAT,
      IN iReactor2StirMotor INT UNSIGNED, IN iReactor2RaditationDetector FLOAT, IN iReactor3SetPosition VARCHAR(30), IN iReactor3ActualPosition VARCHAR(30), IN iReactor3SetY INT,
      IN iReactor3ActualY INT, IN iReactor3RobotStatus VARCHAR(30), IN iReactor3RobotError INT UNSIGNED, IN iReactor3RobotControl INT UNSIGNED, IN iReactor3RobotCheck INT UNSIGNED,
      IN iReactor3SetUp BOOL, IN iReactor3SetDown BOOL, IN iReactor3Up BOOL, IN iReactor3Down BOOL, IN iReactor3Stopcock1Position VARCHAR(4), IN iReactor3Collet1On BOOL,
      IN iReactor3Collet1SetTemperature FLOAT, IN iReactor3Collet1ActualTemperature FLOAT, IN iReactor3Collet2On BOOL, IN iReactor3Collet2SetTemperature FLOAT,
      IN iReactor3Collet2ActualTemperature FLOAT, IN iReactor3Collet3On BOOL, IN iReactor3Collet3SetTemperature FLOAT, IN iReactor3Collet3ActualTemperature FLOAT,
      IN iReactor3StirMotor INT UNSIGNED, IN iReactor3RaditationDetector FLOAT)
    BEGIN
        -- Insert the entry
        INSERT INTO StatusLog VALUES (NULL, iTimestamp, iVacuumSystemOn, iVacuumSystemPressure, iCoolingSystemOn, iPressureRegulator1SetPressure, iPressureRegulator1ActualPressure,
            iPressureRegulator2SetPressure, iPressureRegulator2ActualPressure, iGasTransferValveOpen, iF18LoadValveOpen, iHPLCLoadValveOpen, iReagentRobotPositionSet,
            iReagentRobotPositionActual, iReagentRobotPositionSetX, iReagentRobotPositionSetY, iReagentRobotPositionActualX, iReagentRobotPositionActualY, iReagentRobotStatusX,
            iReagentRobotStatusY, iReagentRobotErrorX, iReagentRobotErrorY, iReagentRobotControlX, iReagentRobotControlY, iReagentRobotCheckX, iReagentRobotCheckY, iGripperSetUp,
            iGripperSetDown, iGripperSetOpen, iGripperSetClose, iGasTransferSetUp, iGasTransferSetDown, iGripperUp, iGripperDown, iGripperOpen, iGripperClose, iGasTransferUp,
            iGasTransferDown,iReactor1SetPosition, iReactor1ActualPosition, iReactor1SetY, iReactor1ActualY, iReactor1RobotStatus, iReactor1RobotError, iReactor1RobotControl, 
            iReactor1RobotCheck, iReactor1SetUp, iReactor1SetDown, iReactor1Up, iReactor1Down, iReactor1Stopcock1Position, iReactor1Stopcock2Position, iReactor1Stopcock3Position,
            iReactor1Collet1On, iReactor1Collet1SetTemperature, iReactor1Collet1ActualTemperature, iReactor1Collet2On, iReactor1Collet2SetTemperature, 
            iReactor1Collet2ActualTemperature, iReactor1Collet3On, iReactor1Collet3SetTemperature, iReactor1Collet3ActualTemperature, iReactor1StirMotor, 
            iReactor1RaditationDetector, iReactor2SetPosition, iReactor2ActualPosition, iReactor2SetY, iReactor2ActualY, iReactor2RobotStatus, iReactor2RobotError, 
            iReactor2RobotControl, iReactor2RobotCheck, iReactor2SetUp, iReactor2SetDown, iReactor2Up, iReactor2Down, iReactor2Stopcock1Position, iReactor2Collet1On,
            iReactor2Collet1SetTemperature, iReactor2Collet1ActualTemperature, iReactor2Collet2On, iReactor2Collet2SetTemperature, iReactor2Collet2ActualTemperature, 
            iReactor2Collet3On, iReactor2Collet3SetTemperature, iReactor2Collet3ActualTemperature, iReactor2StirMotor, iReactor2RaditationDetector, iReactor3SetPosition, 
            iReactor3ActualPosition, iReactor3SetY, iReactor3ActualY, iReactor3RobotStatus, iReactor3RobotError, iReactor3RobotControl, iReactor3RobotCheck, iReactor3SetUp,
            iReactor3SetDown, iReactor3Up, iReactor3Down, iReactor3Stopcock1Position, iReactor3Collet1On, iReactor3Collet1SetTemperature, iReactor3Collet1ActualTemperature,
            iReactor3Collet2On, iReactor3Collet2SetTemperature, iReactor3Collet2ActualTemperature, iReactor3Collet3On, iReactor3Collet3SetTemperature,
            iReactor3Collet3ActualTemperature, iReactor3StirMotor, iReactor3RaditationDetector);
    END //

/* Gets any logs in the SystemLog and RunLog tables that are more recent than the timestamp:
 *   IN Level - Log message level
 *   IN Timestamp - Timestamp to specify when to start returning log messages
 */
DROP PROCEDURE IF EXISTS GetRecentLogsByTimestamp;
CREATE PROCEDURE GetRecentLogsByTimestamp(IN iLevel INT UNSIGNED, IN iTimestamp TIMESTAMP)
    BEGIN
        -- Create a temporary table to hold the logs
        DROP TEMPORARY TABLE IF EXISTS tmp_Logs;
        CREATE TEMPORARY TABLE tmp_Logs
        (
            LogID INT UNSIGNED NOT NULL,
            Date TIMESTAMP NOT NULL,
            Level INT UNSIGNED NOT NULL,
            UserID INT UNSIGNED NOT NULL,
            SequenceID INT UNSIGNED,
            ComponentID INT UNSIGNED,
            Message VARCHAR(1024) NOT NULL
        ) ENGINE=Memory COMMENT="Temporary logs";

        -- Insert the system logs into the temporary table
        INSERT INTO tmp_Logs SELECT LogID, Date, Level, UserID, 0, 0, Message FROM SystemLog WHERE (Level <= iLevel) AND (Date >= iTimestamp) ORDER BY Date DESC, LogID DESC;

        -- Insert the run logs into the temporary table
        INSERT INTO tmp_Logs SELECT LogID, Date, Level, UserID, SequenceID, ComponentID, Message FROM RunLog WHERE (Level <= iLevel) AND (Date >= iTimestamp) ORDER BY Date DESC, LogID DESC;

        -- Return the most recent messages
        SELECT tmp_Logs.LogID, tmp_Logs.Date, tmp_Logs.Level, Users.Username, tmp_Logs.SequenceID, tmp_Logs.ComponentID, tmp_Logs.Message FROM tmp_Logs, Users WHERE tmp_Logs.UserID = Users.UserID ORDER BY Date DESC, LogID DESC;
    END //

/* Gets the N most recent logs from the SystemLog and RunLog tables:
 *   IN Level - Log message level
 *   IN Count - Maximum number of log messages to return
 */
DROP PROCEDURE IF EXISTS GetRecentLogsByCount;
CREATE PROCEDURE GetRecentLogsByCount(IN iLevel INT UNSIGNED, IN iCount INT UNSIGNED)
    BEGIN
        -- Create a temporary table to hold the logs
        DROP TEMPORARY TABLE IF EXISTS tmp_Logs;
        CREATE TEMPORARY TABLE tmp_Logs
        (
            LogID INT UNSIGNED NOT NULL,
            Date TIMESTAMP NOT NULL,
            Level INT UNSIGNED NOT NULL,
            UserID INT UNSIGNED NOT NULL,
            SequenceID INT UNSIGNED,
            ComponentID INT UNSIGNED,
            Message VARCHAR(1024) NOT NULL
        ) ENGINE=Memory COMMENT="Temporary logs";

        -- Insert the system logs into the temporary table
        SET @sql = concat('INSERT INTO tmp_Logs SELECT LogID, Date, Level, UserID, 0, 0, Message FROM SystemLog WHERE Level <= ', iLevel, ' ORDER BY Date DESC, LogID DESC LIMIT ', iCount);
        PREPARE statement FROM @sql;
        EXECUTE statement;
        DROP PREPARE statement;

        -- Insert the run logs into the temporary table
        SET @sql = concat('INSERT INTO tmp_Logs SELECT LogID, Date, Level, UserID, SequenceID, ComponentID, Message FROM RunLog WHERE Level <= ', iLevel, ' ORDER BY Date DESC, LogID DESC LIMIT ', iCount);
        PREPARE statement FROM @sql;
        EXECUTE statement;
        DROP PREPARE statement;

        -- Return the most recent messages
        SET @sql = concat('SELECT tmp_Logs.LogID, tmp_Logs.Date, tmp_Logs.Level, Users.Username, tmp_Logs.SequenceID, tmp_Logs.ComponentID, tmp_Logs.Message FROM tmp_Logs, Users WHERE  tmp_Logs.UserID = Users.UserID ORDER BY Date DESC, LogID DESC LIMIT ', iCount);
        PREPARE statement FROM @sql;
        EXECUTE statement;
        DROP PREPARE statement;
    END //

/****************************************************************************************************************************************************************
 ** Roles *******************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Get a list of roles */
DROP PROCEDURE IF EXISTS GetAllRoles;
CREATE PROCEDURE GetAllRoles()
    BEGIN
        -- Fetch the roles
        SELECT * FROM Roles;
    END //

/* Get a specific role:
 *   IN Rolename - Name of the role
 */
DROP PROCEDURE IF EXISTS GetRole;
CREATE PROCEDURE GetRole(IN iRoleName VARCHAR(30))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Fetch the roles
        CALL Internal_GetRoleID(iRoleName, lRoleID);
        SELECT * FROM Roles WHERE RoleID = lRoleID;
    END //

/* Create a new role:
 *   IN Rolename - Name of the role
 *   IN Flags - Flags describing the role permissions
 */
DROP PROCEDURE IF EXISTS CreateRole;
CREATE PROCEDURE CreateRole(IN iRoleName VARCHAR(30), IN iFlags INT UNSIGNED)
    BEGIN
        -- Create the role
        INSERT INTO Roles VALUES (NULL, iRoleName, iFlags);
    END //

/* Updates an existing role:
 *   IN Rolename - Name of the existing role
 *   IN UpdatedRolename - Name of the updated role
 *   IN UpdatedFlags - Flags describing the updated role permissions
 */
DROP PROCEDURE IF EXISTS UpdateRole;
CREATE PROCEDURE UpdateRole(IN iRoleName VARCHAR(30), IN iUpdatedRoleName VARCHAR(30), IN iUpdatedFlags INT UNSIGNED)
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Update the role
        CALL Internal_GetRoleID(iRoleName, lRoleID);
        UPDATE Roles SET RoleName = iUpdatedRoleName, Flags = iUpdatedFlags WHERE RoleID = lRoleID;
    END //

/* Deletes an existing role:
 *   IN Rolename - Name of the existing role
 */
DROP PROCEDURE IF EXISTS DeleteRole;
CREATE PROCEDURE DeleteRole(IN iRoleName VARCHAR(30))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Delete the role
        CALL Internal_GetRoleID(iRoleName, lRoleID);
        DELETE FROM Roles WHERE RoleID = lRoleID;
    END //

/****************************************************************************************************************************************************************
 ** Users *******************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets information about all system users */
DROP PROCEDURE IF EXISTS GetAllUsers;
CREATE PROCEDURE GetAllUsers()
    BEGIN
        DECLARE lUserID INT UNSIGNED;
        DECLARE lUsername VARCHAR(30);
        DECLARE lFirstName VARCHAR(20);
        DECLARE lLastName VARCHAR(20);
        DECLARE lRoleName VARCHAR(30);
        DECLARE lEmail VARCHAR(30);
        DECLARE lPhone VARCHAR(20);
        DECLARE lMessageLevel INT UNSIGNED;
        DECLARE lNoMoreRows BOOLEAN default FALSE;
        DECLARE lUsersCursor CURSOR FOR SELECT UserID FROM Users;

        -- Declare exception handler
        DECLARE CONTINUE HANDLER FOR NOT FOUND
            SET lNoMoreRows = TRUE;

        -- Create a temporary table to hold the users
        DROP TEMPORARY TABLE IF EXISTS tmp_Users;
        CREATE TEMPORARY TABLE tmp_Users
        (
            Username VARCHAR(30) NOT NULL,
            FirstName VARCHAR(20) NOT NULL,
            LastName VARCHAR(20) NOT NULL,
            RoleName VARCHAR(30) NOT NULL,
            Email VARCHAR(30) NOT NULL,
            Phone VARCHAR(20) NOT NULL,
            MessageLevel INT UNSIGNED NOT NULL
        ) ENGINE=Memory COMMENT="Temporary users";

        -- Open the cursor
        OPEN lUsersCursor;

        -- Iterate over the users and fill our temporary table
        UsersLoop: LOOP
            -- Get the next username
            FETCH lUsersCursor INTO lUserID;

            -- Break out of the loop if we failed to get a username
            IF lNoMoreRows THEN
                CLOSE lUsersCursor;
                LEAVE UsersLoop;
            END IF;

            -- Call the internal function and insert into the temporary table
            CALL Internal_GetUserByID(lUserID, lUsername, lFirstName, lLastName, lRoleName, lEmail, lPhone, lMessageLevel);
            INSERT INTO tmp_Users VALUES (lUsername, lFirstName, lLastName, lRoleName, lEmail, lPhone, lMessageLevel);
        END LOOP UsersLoop;

        -- Return the result set
        SELECT * FROM tmp_Users;
    END //

/* Gets information about the specified user:
 *   IN Username - Name of the user
 */
DROP PROCEDURE IF EXISTS GetUser;
CREATE PROCEDURE GetUser(IN iUsername VARCHAR(30))
    BEGIN
        DECLARE lFirstName VARCHAR(20);
        DECLARE lLastName VARCHAR(20);
        DECLARE lRoleID INT UNSIGNED;
        DECLARE lRoleName VARCHAR(30);
        DECLARE lEmail VARCHAR(30);
        DECLARE lPhone VARCHAR(20);
        DECLARE lMessageLevel INT UNSIGNED;

        -- Create a temporary table to hold the user data
        DROP TEMPORARY TABLE IF EXISTS tmp_User;
        CREATE TEMPORARY TABLE tmp_User
        (
            Username VARCHAR(30) NOT NULL,
            FirstName VARCHAR(20) NOT NULL,
            LastName VARCHAR(20) NOT NULL,
            RoleName VARCHAR(30) NOT NULL,
            Email VARCHAR(30) NOT NULL,
            Phone VARCHAR(20) NOT NULL,
            MessageLevel INT UNSIGNED NOT NULL
        ) ENGINE=Memory COMMENT="Temporary user data";

        -- Call the internal function
        CALL Internal_GetUserByName(iUsername, lFirstName, lLastName, lRoleName, lEmail, lPhone, lMessageLevel);

        -- Fill and return the user result set
        INSERT INTO tmp_User VALUES (iUsername, lFirstName, lLastName, lRoleName, lEmail, lPhone, lMessageLevel);
        SELECT * FROM tmp_User WHERE Username = iUsername;
    END //

/* Gets the password hash for the user:
 *   IN Username - Name of the user
 */
DROP PROCEDURE IF EXISTS GetUserPasswordHash;
CREATE PROCEDURE GetUserPasswordHash(IN iUsername VARCHAR(30))
    BEGIN
        SELECT Password FROM Users WHERE Username = iUsername;
    END //

/* Creates a new user:
 *   
 *   IN Username - Username
 *   IN Password - Hash of the user's password
 *   IN FirstName - User's first name
 *   IN LastName - User's last name
 *   IN RoleName - User's role
 *   IN Email - User's email
 *   IN Phont - User's phone
 *   IN MessageLevel - Message log level (0-2)
 *   IN ClientState - Initial user state
 */
DROP PROCEDURE IF EXISTS CreateUser;
CREATE PROCEDURE CreateUser(IN iUsername VARCHAR(30), IN iPassword VARCHAR(30), IN iFirstName VARCHAR(20), IN iLastName VARCHAR(20), 
      IN iRoleName VARCHAR(20), IN iEmail VARCHAR(30), IN iPhone VARCHAR(20), IN iMessageLevel INT UNSIGNED, IN iClientState VARCHAR(2048))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Look up the role ID
        CALL Internal_GetRoleID(iRoleName, lRoleID);

        -- Create the user
        INSERT INTO Users VALUES (NULL, iUsername, iPassword, iFirstName, iLastName, lRoleID, iEmail, iPhone, iMessageLevel, iClientState);
    END //

/* Updates an existing user:
 *   IN Username - Username of the user to update
 *   IN FirstName - User's first name
 *   IN LastName - User's last name
 *   IN RoleName - User's role
 *   IN Email - User's email
 *   IN Phont - User's phone
 *   IN MessageLevel - Message log level (0-2)
 */
DROP PROCEDURE IF EXISTS UpdateUser;
CREATE PROCEDURE UpdateUser(IN iUsername VARCHAR(30), IN iFirstName VARCHAR(20), IN iLastName VARCHAR(20), IN iRoleName VARCHAR(20), 
      IN iEmail VARCHAR(30), IN iPhone VARCHAR(20), IN iMessageLevel INT UNSIGNED)
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Look up the role ID
        CALL Internal_GetRoleID(iRoleName, lRoleID);

        -- Update the user
        UPDATE Users SET FirstName = iFirstName, LastName = iLastName, RoleID = lRoleID, Email = iEmail, Phone = iPhone, 
          MessageLevel = iMessageLevel WHERE Username = iUsername;
    END //
 
/* Updates a user's password:
 *   IN Username - Username of the user to update
 *   IN Password - Hash of the user's password
 */
DROP PROCEDURE IF EXISTS UpdateUserPassword;
CREATE PROCEDURE UpdateUserPassword(IN iUsername VARCHAR(30), IN iPassword VARCHAR(30))
    BEGIN
        -- Update the user
        UPDATE Users SET Password = iPassword WHERE Username = iUsername;
    END //

/* Deletes a user:
 *   IN Username - Username of the user to delete
 */
DROP PROCEDURE IF EXISTS DeleteUser;
CREATE PROCEDURE DeleteUser(IN iUsername VARCHAR(30))
    BEGIN
        -- Delete the user
        DELETE FROM Users WHERE Username = iUsername;
    END //

/* Returns the client state of a user:
 *   IN Username - Username
 */
DROP PROCEDURE IF EXISTS GetUserClientState;
CREATE PROCEDURE GetUserClientState(IN iUsername VARCHAR(30))
    BEGIN
        -- Return the user's client state
        SELECT ClientState FROM Users WHERE Username = iUsername;
    END //

/* Updates the client state of a user:
 *   IN Username - Username
 *   IN ClientState - String describing the state of the client
 */
DROP PROCEDURE IF EXISTS UpdateUserClientState;
CREATE PROCEDURE UpdateUserClientState(IN iUsername VARCHAR(30), IN iClientState VARCHAR(2048))
    BEGIN
        -- Save the user's client state
        UPDATE Users SET ClientState = iClientState WHERE Username = iUsername;
    END //

/****************************************************************************************************************************************************************
 ** Sequences ***************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Get a list of sequences:
 *   IN Type - Type of sequence to return (either "Saved", "History" or "" for both)
 */

CREATE PROCEDURE `GetAllSequencesByName`(IN iName VARCHAR(100))
    BEGIN
        
        IF iName != "" THEN
            
            SELECT Sequences.SequenceID, Sequences.Name, Sequences.Comment, Sequences.Type, Sequences.CreationDate, Users.Username, Sequences.FirstComponentID,
                Sequences.ComponentCount, Sequences.Valid, Sequences.Dirty FROM Sequences, Users WHERE Sequences.Name = iName AND Sequences.UserID = Users.UserID
                AND Sequences.Type = "Saved";
        END IF;
    END //


CREATE PROCEDURE `GetAllHistorySequencesByName`(IN iName VARCHAR(100))
    BEGIN
        
        IF iName != "" THEN
            
            SELECT Sequences.SequenceID, Sequences.Name, Sequences.Comment, Sequences.Type, Sequences.CreationDate, Users.Username, Sequences.FirstComponentID,
                Sequences.ComponentCount, Sequences.Valid, Sequences.Dirty FROM Sequences, Users WHERE Sequences.Name = iName AND Sequences.UserID = Users.UserID
                AND Sequences.Type = "History";
        END IF;
    END //

DROP PROCEDURE IF EXISTS GetAllSequences;
CREATE PROCEDURE GetAllSequences(IN iType VARCHAR(20))
    BEGIN
        -- Check if we have a type
        IF iType != "" THEN
            -- Yes, so filter the sequences based on type and replace the user IDs with names
            SELECT Sequences.SequenceID, Sequences.Name, Sequences.Comment, Sequences.Type, Sequences.CreationDate, Users.Username, Sequences.FirstComponentID,
                Sequences.ComponentCount, Sequences.Valid, Sequences.Dirty FROM Sequences, Users WHERE Sequences.Type = iType AND Sequences.UserID = Users.UserID;
        ELSE
            -- No, so return all sequences and replace the user IDs with names
            SELECT Sequences.SequenceID, Sequences.Name, Sequences.Comment, Sequences.Type, Sequences.CreationDate, Users.Username, Sequences.FirstComponentID,
                Sequences.ComponentCount, Sequences.Valid, Sequences.Dirty FROM Sequences, Users WHERE Sequences.UserID = Users.UserID;
        END IF;
    END //

/* Get a sequence:
 *   IN SequenceID - ID of the sequence to get
 */
DROP PROCEDURE IF EXISTS GetSequence;
CREATE PROCEDURE GetSequence(IN iSequenceID INT UNSIGNED)
    BEGIN
        -- Filter the sequences based on type and replace the user IDs with names
        SELECT Sequences.SequenceID, Sequences.Name, Sequences.Comment, Sequences.Type, Sequences.CreationDate, Users.Username, Sequences.FirstComponentID,
            Sequences.ComponentCount, Sequences.Valid, Sequences.Dirty FROM Sequences, Users WHERE Sequences.SequenceID = iSequenceID AND Sequences.UserID = Users.UserID;
    END //

/* Create a new sequence:
 *   IN Name - Name of the new sequence
 *   IN Comment - Comment associated with the new sequence
 *   IN Type - Type of the sequence (either "Saved" or "Manual")
 *   IN Username - Username of the user creating the new sequence
 *   IN Cassettes - Number of cassettes in the new sequence
 *   IN Reagents - Number of reagents per cassette
 *   IN Columns - Number of columns per cassette
 *   OUT SequenceID - ID of the new sequence
 */
DROP PROCEDURE IF EXISTS CreateSequence;
CREATE PROCEDURE CreateSequence(IN iName VARCHAR(64), IN iComment VARCHAR(255), IN iType VARCHAR(20), IN iUsername VARCHAR(30), IN iCassettes INT UNSIGNED,
                                IN iReagents INT UNSIGNED, IN iColumns INT UNSIGNED, OUT oSequenceID INT UNSIGNED)
    BEGIN
        DECLARE lUserID INT UNSIGNED;
        DECLARE lSequenceID INT UNSIGNED;
        DECLARE lCassetteID INT UNSIGNED;
        DECLARE lReagentID INT UNSIGNED;
        DECLARE lCassette INT UNSIGNED default 0;
        DECLARE lReagent INT UNSIGNED;
        DECLARE lColumn INT UNSIGNED;
        DECLARE lCassetteJSON VARCHAR(1024);

        -- Look up the user ID
        SET lUserID = (SELECT UserID FROM Users WHERE Username = iUsername);

        -- Create the entry in the sequences table
        INSERT INTO Sequences VALUES (NULL, iName, iComment, iType, NULL, lUserID, 0, 0, True, False);
        SET lSequenceID = LAST_INSERT_ID();

        -- Create each cassette
        WHILE lCassette < iCassettes DO
            -- Create the cassette
            CALL CreateComponent(lSequenceID, "CASSETTE", "", "", lCassetteID);

            -- Update the sequence table reference if this is the first cassette
            IF lCassette = 0 THEN
                UPDATE Sequences SET FirstComponentID = lCassetteID WHERE SequenceID = lSequenceID;
            END IF;

            -- Start the cassette JSON string
            SET lCassetteJSON = CONCAT("{\"type\":\"component\", \"componenttype\":\"CASSETTE\", \"reactor\":", lCassette + 1, ", \"reagentids\":[");

            -- Create the reagents
            SET lReagent = 0;
            WHILE lReagent < iReagents DO
                -- Create an entry in the reagents table
                INSERT INTO Reagents VALUES (NULL, lSequenceID, lCassetteID, lReagent + 1, "", "");
                SET lReagentID = LAST_INSERT_ID();

                -- Update the cassette JSON string
                IF lReagent = 0 THEN
                    SET lCassetteJSON = CONCAT(lCassetteJSON, lReagentID);
                ELSE
                    SET lCassetteJSON = CONCAT(lCassetteJSON, ", ", lReagentID);
                END IF;

                -- Increment the reagent counter
                SET lReagent = lReagent + 1;
            END WHILE;

            -- Create the columns
            SET lColumn = 0; 
            WHILE lColumn < iColumns DO
                -- Create an entry in the reagents table
                INSERT INTO Reagents VALUES (NULL, lSequenceID, lCassetteID, CHAR(ASCII('A') + lColumn), "", "");
                SET lReagentID = LAST_INSERT_ID();

                -- Update the cassette JSON string
                SET lCassetteJSON = CONCAT(lCassetteJSON, ", ", lReagentID);

                -- Increment the column counter
                SET lColumn = lColumn + 1;
            END WHILE;

            -- Finish the cassette JSON string
            SET lCassetteJSON = CONCAT(lCassetteJSON, "]}");

            -- Update the cassette JSON string
            CALL UpdateComponent(lCassetteID, "CASSETTE", "", lCassetteJSON);

            -- Increment the cassette counter
            SET lCassette = lCassette + 1;
        END WHILE;

        -- Set the dirty flag now that the sequence is complete
        UPDATE Sequences SET Dirty = True WHERE SequenceID = lSequenceID;

        -- Return the sequence ID
        SET oSequenceID = lSequenceID;
    END //

/* Updates an existing sequence:
 *   IN SequenceID - ID of the sequence to update
 *   IN Name - Name of the sequence
 *   IN Comment - Comment associated with the sequence *   IN Valid - Flag indicating if this sequence is valid
 */
DROP PROCEDURE IF EXISTS UpdateSequence;
CREATE PROCEDURE UpdateSequence(IN iSequenceID INT UNSIGNED, IN iName VARCHAR(64), IN iComment VARCHAR(255), IN iValid BOOL)
    BEGIN
        -- Update the sequence
        UPDATE Sequences SET Name = iName, Comment = iComment, Valid = iValid WHERE SequenceID = iSequenceID;
    END //

/* Updates the dirty flag on an existing sequence:
 *   IN SequenceID - ID of the sequence to update
 *   IN Dirty - Flag indicating if the sequence validation is dirty
 */
DROP PROCEDURE IF EXISTS UpdateSequenceDirtyFlag;
CREATE PROCEDURE UpdateSequenceDirtyFlag(IN iSequenceID INT UNSIGNED, IN iDirty BOOL)
    BEGIN
        -- Update the sequence
        UPDATE Sequences SET Dirty = iDirty WHERE SequenceID = iSequenceID;
    END //

/* Deletes a sequence:
 *   IN SequenceID - ID of the sequence to delete
 */
DROP PROCEDURE IF EXISTS DeleteSequence;
CREATE PROCEDURE DeleteSequence(IN iSequenceID INT UNSIGNED)
    BEGIN
        -- Delete the sequence reagents
        DELETE FROM Reagents WHERE SequenceID = iSequenceID;

        -- Delete the sequence components
        DELETE FROM Components WHERE SequenceID = iSequenceID;

        -- Delete the sequence
        DELETE FROM Sequences WHERE SequenceID = iSequenceID;
    END //

/****************************************************************************************************************************************************************
 ** Reagents ****************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets a reagent:
 *   IN ReagentID - ID of the reagent
 */
DROP PROCEDURE IF EXISTS GetReagent;
CREATE PROCEDURE GetReagent(IN iReagentID INT UNSIGNED)
    BEGIN
        -- Look up the reagent
        SELECT * FROM Reagents WHERE ReagentID = iReagentID;
    END //

/* Gets all reagents in the given sequence:
 *   IN SequenceID - ID of the sequence
 */
DROP PROCEDURE IF EXISTS GetReagentsBySequence;
CREATE PROCEDURE GetReagentsBySequence(IN iSequenceID INT UNSIGNED)
    BEGIN
        -- Look up the reagents
        SELECT * FROM Reagents WHERE SequenceID = iSequenceID;
    END //

/* Gets all reagents in the sequence that match the given name:
 *   IN SequenceID - ID of the sequence
 *   IN Name - Reagent name
 */
DROP PROCEDURE IF EXISTS GetReagentsByName;
CREATE PROCEDURE GetReagentsByName(IN iSequenceID INT UNSIGNED, IN iName VARCHAR(64))
    BEGIN
        -- Look up the reagents
        SELECT * FROM Reagents WHERE SequenceID = iSequenceID AND Name = iName;
    END //

/* Get the reagent as the specified position:
 *   IN SequenceID - Sequence ID of the reagent
 *   IN CassetteNumber - Cassette number of the reagent
 *   IN Position - Position of the reagent
 */
DROP PROCEDURE IF EXISTS GetReagentByPosition;
CREATE PROCEDURE GetReagentByPosition(IN iSequenceID INT UNSIGNED, IN iCassetteNumber INT UNSIGNED, IN iPosition VARCHAR(2))
    BEGIN
        DECLARE lComponentID INT UNSIGNED;
        DECLARE lReagentID INT UNSIGNED;

        -- Look up the component ID of the cassette
        CALL Internal_GetComponentByOffset(iSequenceID, iCassetteNumber - 1, lComponentID);

        -- Look up the reagent by position
        SELECT * FROM Reagents WHERE SequenceID = iSequenceID AND ComponentID = lComponentID AND Position = iPosition;
    END //

/* Get the cassette number that contains the given reagent:
 *   IN SequenceID - Sequence ID of the reagent
 *   IN ReagentID - ID of the reagent
 *   OUT Cassette - Cassette that contains the reagent
 */
DROP PROCEDURE IF EXISTS GetReagentCassette;
CREATE PROCEDURE GetReagentCassette(IN iSequenceID INT UNSIGNED, IN iReagentID INT UNSIGNED, OUT oCassette INT UNSIGNED)
    BEGIN
        DECLARE lComponentID INT UNSIGNED;
        DECLARE lComponentOffset INT UNSIGNED;

        -- Look up the offset of the reagent's component ID
        SET lComponentID = (SELECT ComponentID FROM Reagents WHERE SequenceID = iSequenceID AND ReagentID = iReagentID);
        CALL Internal_GetOffsetByComponent(iSequenceID, lComponentID, lComponentOffset);

        -- Set the return value
        SET oCassette = lComponentOffset + 1;
    END //

/* Update an existing reagent:
 *   IN ReagentID - ID of the reagent
 *   IN Name - Reagent name
 *   IN Description - ReagentDescription
 */
DROP PROCEDURE IF EXISTS UpdateReagent;
CREATE PROCEDURE UpdateReagent(IN iReagentID INT UNSIGNED, IN iName VARCHAR(64), IN iDescription VARCHAR(255))
    BEGIN
        -- Update the reagent
        UPDATE Reagents SET Name = iName, Description = iDescription WHERE ReagentID = iReagentID;
    END //

/* Updates an existing reagent by position:
 *   IN SequenceID - Sequence ID of the reagent
 *   IN CassetteNumber - Cassette number of the reagent
 *   IN Position - Position of the reagent
 *   IN Name - Reagent name
 *   IN Description - ReagentDescription
 */
DROP PROCEDURE IF EXISTS UpdateReagentByPosition;
CREATE PROCEDURE UpdateReagentByPosition(IN iSequenceID INT UNSIGNED, IN iCassetteNumber INT UNSIGNED, IN iPosition VARCHAR(2), IN iName VARCHAR(64),
                                         IN iDescription VARCHAR(255))
    BEGIN
        DECLARE lComponentID INT UNSIGNED;
        DECLARE lReagentID INT UNSIGNED;

        -- Look up the component ID of the cassette
        CALL Internal_GetComponentByOffset(iSequenceID, iCassetteNumber - 1, lComponentID);

        -- Look up the reagent ID by position
        SET lReagentID = (SELECT ReagentID FROM Reagents WHERE SequenceID = iSequenceID AND ComponentID = lComponentID AND Position = iPosition);

        -- Update the reagent by position
        CALL UpdateReagent(lReagentID, iName, iDescription);
    END //

/****************************************************************************************************************************************************************
 ** Components **************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets a component:
 *   IN ComponentID - ID of the component
 */
DROP PROCEDURE IF EXISTS GetComponent;
CREATE PROCEDURE GetComponent(IN iComponentID INT UNSIGNED)
    BEGIN
        -- Return the component
        SELECT * FROM Components WHERE ComponentID = iComponentID;
    END //

/* Looks up a cassette component by offset:
 *   IN SequenceID - ID of the sequence containing the cassette
 *   IN CassetteOffset - Cassette offset
 */
DROP PROCEDURE IF EXISTS GetCassette;
CREATE PROCEDURE GetCassette(IN iSequenceID INT UNSIGNED, IN iCassetteOffset INT UNSIGNED)
    BEGIN
        DECLARE lCassetteID INT UNSIGNED;

        -- Get the cassette component ID
        CALL Internal_GetComponentByOffset(iSequenceID, iCassetteOffset, lCassetteID);

        -- Return the cassette
        SELECT * FROM Components WHERE ComponentID = lCassetteID;
    END //

/* Gets all of the components associated with the given sequence ID: *   IN SequenceID - ID of the sequence
 */
DROP PROCEDURE IF EXISTS GetComponentsBySequence;
CREATE PROCEDURE GetComponentsBySequence(IN iSequenceID INT UNSIGNED)
    BEGIN
        DECLARE lComponentID INT UNSIGNED;
        DECLARE lPreviousComponentID INT UNSIGNED;
        DECLARE lNextComponentID INT UNSIGNED;
        DECLARE lType VARCHAR(20);
        DECLARE lNote VARCHAR(64);
        DECLARE lDetails VARCHAR(2048);

        -- Create a temporary table to hold the component data
        DROP TEMPORARY TABLE IF EXISTS tmp_Components;
        CREATE TEMPORARY TABLE tmp_Components
        (
            ComponentID INT UNSIGNED NOT NULL,
            SequenceID INT UNSIGNED NOT NULL,
            PreviousComponentID INT UNSIGNED NOT NULL,
            NextComponentID INT UNSIGNED NOT NULL,
            Type VARCHAR(20) NOT NULL,
            Note VARCHAR(64),
            Details VARCHAR(2048) NOT NULL
        ) ENGINE=Memory COMMENT="Temporary component data";

        -- Get the first component ID in the sequence
        CALL Internal_GetFirstComponent(iSequenceID, lComponentID);

        -- Load the components in order
        WHILE lComponentID > 0 DO
            -- Load the component data from the Components table
            SELECT PreviousComponentID FROM Components WHERE ComponentID = lComponentID INTO lPreviousComponentID;
            SELECT NextComponentID FROM Components WHERE ComponentID = lComponentID INTO lNextComponentID;
            SELECT Type FROM Components WHERE ComponentID = lComponentID INTO lType;
            SELECT Note FROM Components WHERE ComponentID = lComponentID INTO lNote;
            SELECT Details FROM Components WHERE ComponentID = lComponentID INTO lDetails;

            -- Save the component in our temporary table
            INSERT INTO tmp_Components VALUES (lComponentID, iSequenceID, lPreviousComponentID, lNextComponentID, lType, lNote, lDetails);

            -- Get the next component ID
            CALL Internal_GetNextComponent(lComponentID, lComponentID);
        END WHILE;

        -- Return the temporary components
        SELECT * FROM tmp_Components;
    END //

/* Creates a new component and inserts it at the end of a sequence:
 *   IN SequenceID - ID of the sequence
 *   IN Type - Type of the component
 *   IN Note - Note associated with the component
 *   IN Details - Component details
 *   OUT ComponentID - ID of the new component
 */
DROP PROCEDURE IF EXISTS CreateComponent;
CREATE PROCEDURE CreateComponent(IN iSequenceID INT UNSIGNED, IN iType VARCHAR(20), IN iNote VARCHAR(64), IN iDetails VARCHAR(2048), OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lLastComponentID INT UNSIGNED;

        -- Get the ID of the last component in the sequence
        CALL Internal_GetLastComponent(iSequenceID, lLastComponentID);

        -- Insert the component
        CALL InsertComponent(iSequenceID, iType, iNote, iDetails, lLastComponentID, oComponentID);
    END //

/* Creates a new component and inserts it at the desired location in a sequence:
 *   IN SequenceID - ID of the sequence
 *   IN Type - Type of the component
 *   IN Note - Note associated with the component
 *   IN Details - Component details
 *   IN InsertID - ID of the component to insert after
 *   OUT ComponentID - ID of the new component
 */
DROP PROCEDURE IF EXISTS InsertComponent;
CREATE PROCEDURE InsertComponent(IN iSequenceID INT UNSIGNED, IN iType VARCHAR(20), IN iNote VARCHAR(64), IN iDetails VARCHAR(2048), IN iInsertID INT UNSIGNED, 
                                 OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lUserID INT UNSIGNED;
        DECLARE lNextComponentID INT UNSIGNED;
        DECLARE lComponentCount INT UNSIGNED;

        -- Get the component after the insert position
        CALL Internal_GetNextComponent(iInsertID, lNextComponentID);
        IF lNextComponentID IS NULL THEN
            SET lNextComponentID = 0;
        END IF;

        -- Add the component
        INSERT INTO Components VALUES (NULL, iSequenceID, iInsertID, lNextComponentID, iType, iNote, iDetails);
        SET oComponentID = LAST_INSERT_ID();

        -- Update the previous and next components
        UPDATE Components SET NextComponentID = oComponentID WHERE ComponentID = iInsertID;
        UPDATE Components SET PreviousComponentID = oComponentID WHERE ComponentID = lNextComponentID;

        -- Update the sequences's component count
        SET lComponentCount = (SELECT ComponentCount FROM Sequences WHERE SequenceID = iSequenceID) + 1;
        UPDATE Sequences SET ComponentCount = lComponentCount WHERE SequenceID = iSequenceID;
    END //

/* Updates an existing component:
 *   IN ComponentID - ID of the component to update
 *   IN Type - Type of the component
 *   IN Note - Note associated with the component
 *   IN Details - Component details
 */
DROP PROCEDURE IF EXISTS UpdateComponent;
CREATE PROCEDURE UpdateComponent(IN iComponentID INT UNSIGNED, IN iType VARCHAR(20), IN iNote VARCHAR(64), IN iDetails VARCHAR(2048))
    BEGIN
        -- Update the component
        UPDATE Components SET Type = iType, Note = iNote, Details = iDetails WHERE ComponentID = iComponentID;
    END //

/* Moves an existing component:
 *   IN ComponentID - ID of the component to update
 *   IN InsertAfterID - ID of the component that will preceed ComponentID after the move
 */
DROP PROCEDURE IF EXISTS MoveComponent;
CREATE PROCEDURE MoveComponent(IN iComponentID INT UNSIGNED, iInsertAfterID INT UNSIGNED)
    BEGIN
        DECLARE lOldPreviousComponentID INT UNSIGNED;
        DECLARE lOldNextComponentID INT UNSIGNED;
        DECLARE lNewNextComponentID INT UNSIGNED;

        -- Find the old previous component ID
        CALL Internal_GetPreviousComponent(iComponentID, lOldPreviousComponentID);

        -- Skip if we're not moving the component
        IF lOldPreviousComponentID != iInsertAfterID THEN
            -- Find the old and new next component IDs
            CALL Internal_GetNextComponent(iComponentID, lOldNextComponentID);
            CALL Internal_GetNextComponent(iInsertAfterID, lNewNextComponentID);

            -- Remove the component
            UPDATE Components SET NextComponentID = lOldNextComponentID WHERE ComponentID = lOldPreviousComponentID;
            UPDATE Components SET PreviousComponentID = lOldPreviousComponentID WHERE ComponentID = lOldNextComponentID;

            -- Insert the component
           UPDATE Components SET NextComponentID = iComponentID WHERE ComponentID = iInsertAfterID;
           UPDATE Components SET PreviousComponentID = iComponentID WHERE ComponentID = lNewNextComponentID;

           -- Update the component
           UPDATE Components SET PreviousComponentID = iInsertAfterID WHERE ComponentID = iComponentID;
           UPDATE Components SET NextComponentID = lNewNextComponentID WHERE ComponentID = iComponentID;
        END IF;
    END //

/* Deletes the component and removes it from the sequence:
 *   IN ComponentID - ID of the component to delete
 */
DROP PROCEDURE IF EXISTS DeleteComponent;
CREATE PROCEDURE DeleteComponent(IN iComponentID INT UNSIGNED)
    BEGIN
        DECLARE lPreviousComponentID INT UNSIGNED;
        DECLARE lNextComponentID INT UNSIGNED;
        DECLARE lSequenceID INT UNSIGNED;
        DECLARE lComponentCount INT UNSIGNED;

        -- Find the previous and next component IDs
        CALL Internal_GetPreviousComponent(iComponentID, lPreviousComponentID);
        CALL Internal_GetNextComponent(iComponentID, lNextComponentID);

        -- Update the component references
        UPDATE Components SET NextComponentID = lNextComponentID WHERE ComponentID = lPreviousComponentID;
        UPDATE Components SET PreviousComponentID = lPreviousComponentID WHERE ComponentID = lNextComponentID;

        -- Update the sequences's component count
        SET lSequenceID = (SELECT SequenceID FROM Components WHERE ComponentID = iComponentID);
        SET lComponentCount = (SELECT ComponentCount FROM Sequences WHERE SequenceID = lSequenceID) - 1;
        UPDATE Sequences SET ComponentCount = lComponentCount WHERE SequenceID = lSequenceID;

        -- Delete the component
        DELETE FROM Components WHERE ComponentID = iComponentID;
    END //

/****************************************************************************************************************************************************************
 ** Internal procedures *****************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets information about the specified user */
DROP PROCEDURE IF EXISTS Internal_GetUserByName;
CREATE PROCEDURE Internal_GetUserByName(IN iUsername VARCHAR(30), OUT oFirstName VARCHAR(20), OUT oLastName VARCHAR(20), OUT oRoleName VARCHAR(30),
      OUT oEmail VARCHAR(30), OUT oPhone VARCHAR(20), OUT oMessageLevel INT UNSIGNED)
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Fetch the user data
        SELECT FirstName FROM Users WHERE Username = iUsername INTO oFirstName;
        SELECT LastName FROM Users WHERE Username = iUsername INTO oLastName;
        SELECT RoleID FROM Users WHERE Username = iUsername INTO lRoleID;
        SELECT Email FROM Users WHERE Username = iUsername INTO oEmail;
        SELECT Phone FROM Users WHERE Username = iUsername INTO oPhone;
        SELECT MessageLevel FROM Users WHERE Username = iUsername INTO oMessageLevel;

        -- Look up the role name
        SELECT RoleName FROM Roles WHERE RoleID = lRoleID INTO oRoleName;
    END //

/* Gets information about the specified user */
DROP PROCEDURE IF EXISTS Internal_GetUserByID;
CREATE PROCEDURE Internal_GetUserByID(IN iUserID INT UNSIGNED, OUT oUsername VARCHAR(30), OUT oFirstName VARCHAR(20), OUT oLastName VARCHAR(20), OUT oRoleName VARCHAR(30),
      OUT oEmail VARCHAR(30), OUT oPhone VARCHAR(20), OUT oMessageLevel INT UNSIGNED)
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Fetch the user data
        SELECT Username FROM Users WHERE UserID = iUserID INTO oUsername;
        SELECT FirstName FROM Users WHERE UserID = iUserID INTO oFirstName;
        SELECT LastName FROM Users WHERE UserID = iUserID INTO oLastName;
        SELECT RoleID FROM Users WHERE UserID = iUserID INTO lRoleID;
        SELECT Email FROM Users WHERE UserID = iUserID INTO oEmail;
        SELECT Phone FROM Users WHERE UserID = iUserID INTO oPhone;
        SELECT MessageLevel FROM Users WHERE UserID = iUserID INTO oMessageLevel;

        -- Look up the role name
        SELECT RoleName FROM Roles WHERE RoleID = lRoleID INTO oRoleName;
    END //

/* Maps a given role name to an ID */
DROP PROCEDURE IF EXISTS Internal_GetRoleID;
CREATE PROCEDURE Internal_GetRoleID(IN iRoleName VARCHAR(30), OUT oRoleID INT UNSIGNED)
    BEGIN
        -- Look up the role ID
        SELECT RoleID FROM Roles WHERE RoleName = iRoleName INTO oRoleID;
    END //

/* Returns the first component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   OUT ComponentID - ID of the first component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetFirstComponent;
CREATE PROCEDURE Internal_GetFirstComponent(IN iSequenceID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        -- Get the first component ID
        SET oComponentID = (SELECT FirstComponentID FROM Sequences WHERE SequenceID = iSequenceID);
    END //

/* Returns the previous component of a sequence:
 *   IN ComponentID - ID of the current component
 *   OUT ComponentID - ID of the previous component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetPreviousComponent;
CREATE PROCEDURE Internal_GetPreviousComponent(IN iComponentID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        -- Get the previous component ID
        SET oComponentID = (SELECT PreviousComponentID FROM Components WHERE ComponentID = iComponentID);
    END //

/* Returns the next component of a sequence:
 *   IN ComponentID - ID of the current component
 *   OUT ComponentID - ID of the next component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetNextComponent;
CREATE PROCEDURE Internal_GetNextComponent(IN iComponentID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        -- Get the next component ID
        SET oComponentID = (SELECT NextComponentID FROM Components WHERE ComponentID = iComponentID);
    END //

/* Returns the last component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   OUT ComponentID - ID of the last component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetLastComponent;
CREATE PROCEDURE Internal_GetLastComponent(IN iSequenceID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lComponentID INT UNSIGNED;
        DECLARE lNextComponentID INT UNSIGNED;

        -- Get the first and next component IDs
        CALL Internal_GetFirstComponent(iSequenceID, lComponentID);
        CALL Internal_GetNextComponent(lComponentID, lNextComponentID);

        -- Loop until we the next component ID is zero
        WHILE lNextComponentID > 0 DO
            -- Get the next component ID
            SET lComponentID = lNextComponentID;
            CALL Internal_GetNextComponent(lComponentID, lNextComponentID);
        END WHILE;

        -- Return the component ID
        SET oComponentID = lComponentID;
    END //

/* Returns the Nth component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   IN ComponentOffset - Offset of the component
 *   OUT ComponentID - ID of the component
 */
DROP PROCEDURE IF EXISTS Internal_GetComponentByOffset;
CREATE PROCEDURE Internal_GetComponentByOffset(IN iSequenceID INT UNSIGNED, IN iComponentOffset INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lComponentID INT UNSIGNED default 0;
        DECLARE lComponentOffset INT UNSIGNED default 0;

        -- Loop until we reach the desired offset
        WHILE lComponentOffset <= iComponentOffset DO
            IF lComponentOffset = 0 THEN
                -- Get the first component ID
                CALL Internal_GetFirstComponent(iSequenceID, lComponentID);
            ELSE
                -- Get the next component ID
                CALL Internal_GetNextComponent(lComponentID, lComponentID);
            END IF;

            -- Increment the component counter
            SET lComponentOffset = lComponentOffset + 1;
        END WHILE;

        -- Set the return value
        SET oComponentID = lComponentID;
    END //

/* Returns the offset of the given component in the sequence:
 *   IN SequenceID - ID of the sequence
 *   IN ComponentID - ID of the component
 *   OUT ComponentOffset - Offset of the component
 */
DROP PROCEDURE IF EXISTS Internal_GetOffsetByComponent;
CREATE PROCEDURE Internal_GetOffsetByComponent(IN iSequenceID INT UNSIGNED, IN iComponentID INT UNSIGNED, OUT oComponentOffset INT UNSIGNED)
    BEGIN
        DECLARE lComponentID INT UNSIGNED default 0;
        DECLARE lComponentOffset INT UNSIGNED default 0;

        -- Get the first component ID
        CALL Internal_GetFirstComponent(iSequenceID, lComponentID);

        -- Loop until we reach the desired offset
        WHILE lComponentID != iComponentID DO
            -- Increment the component counter
            SET lComponentOffset = lComponentOffset + 1;

            -- Get the next component ID
            CALL Internal_GetNextComponent(lComponentID, lComponentID);
        END WHILE;

        -- Set the return value
        SET oComponentOffset = lComponentOffset;
    END //

-- Restore the delimiter
DELIMITER ;

