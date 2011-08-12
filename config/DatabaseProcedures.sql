/* Create the stored procedures */

/* Drop any existing procedures to allow this file to be reimported as needed */
DROP PROCEDURE IF EXISTS CreateNewRole;
DROP PROCEDURE IF EXISTS CreateNewUser;
DROP PROCEDURE IF EXISTS CreateNewSequence;
DROP PROCEDURE IF EXISTS UpdateReagent;
DROP PROCEDURE IF EXISTS UpdateReagentByPosition;
DROP PROCEDURE IF EXISTS GetReagentByPosition;
DROP PROCEDURE IF EXISTS GetFirstComponent;
DROP PROCEDURE IF EXISTS GetNextComponent;
DROP PROCEDURE IF EXISTS GetComponentByOffset;

/* Change the delimiter for this file */
DELIMITER //

/****************************************************************************************************************************************************************
 ** Roles *******************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Create a new role:
 *   IN Rolename - Name of the role
 *   IN Flags - Flags describing the role permissions
 *   OUT RoleID - ID of the new role
 */
CREATE PROCEDURE CreateNewRole(IN iRoleName VARCHAR(30), IN iFlags INT UNSIGNED, OUT oRoleID INT UNSIGNED)
    BEGIN
        /* Create the role */
        INSERT INTO Roles VALUES (NULL, iRoleName, iFlags);
        SET oRoleID = LAST_INSERT_ID();
    END //

/****************************************************************************************************************************************************************
 ** Users *******************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Create a new user:
 *   IN Username - Username
 *   IN Password - Hash of the user's password
 *   IN FirstName - User's first name
 *   IN LastName - User's last name
 *   IN RoleName - User's role
 *   OUT UserID - ID of the new user
 */
CREATE PROCEDURE CreateNewUser(IN iUsername VARCHAR(30), IN iPassword VARCHAR(30), IN iFirstName VARCHAR(20), IN iLastName VARCHAR(20), IN iRoleName VARCHAR(20),
                               OUT oUserID INT UNSIGNED)
    BEGIN
        /* Look up the role ID */
        DECLARE lRoleID INT UNSIGNED;
        SET lRoleID = (SELECT RoleID FROM Roles WHERE RoleName = iRoleName);

        /* Create the user */
        INSERT INTO Users VALUES (NULL, iUsername, iPassword, iFirstName, iLastName, lRoleID, "");
        SET oUserID = LAST_INSERT_ID();
    END //
 
/****************************************************************************************************************************************************************
 ** Sequences ***************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Create a new sequence:
 *   IN Name - Name of the new sequence
 *   IN Comment - Comment associated with the new sequence
 *   IN Username - Username of the user creating the new sequence
 *   IN Cassettes - Number of cassettes in the new sequence
 *   IN Reagents - Number of reagents per cassette
 *   IN Columns - Number of columns per cassette
 *   OUT SequenceID - ID of the new sequence
 */
CREATE PROCEDURE CreateNewSequence(IN iName VARCHAR(64), IN iComment VARCHAR(255), IN iUsername VARCHAR(30), IN iCassettes INT UNSIGNED, IN iReagents INT UNSIGNED, 
                                   IN iColumns INT UNSIGNED, OUT oSequenceID INT UNSIGNED)
    BEGIN
        /* Declare local variables */
        DECLARE lUserID INT UNSIGNED;
        DECLARE lSequenceID INT UNSIGNED;
        DECLARE lCurrentCassetteID INT UNSIGNED;
        DECLARE lPreviousCassetteID INT UNSIGNED;
        DECLARE lReagentID INT UNSIGNED;
        DECLARE lCassette INT UNSIGNED default 0;
        DECLARE lReagent INT UNSIGNED;
        DECLARE lColumn INT UNSIGNED;
        DECLARE lCassetteJSON VARCHAR(1024);

        /* Look up the user ID */
        SET lUserID = (SELECT UserID FROM Users WHERE Username = iUsername);

        /* Create the entry in the sequences table */
        INSERT INTO Sequences VALUES (NULL, iName, iComment, NULL, lUserID, 0);
        SET lSequenceID = LAST_INSERT_ID();

        /* Create each cassette */
        WHILE lCassette < iCassettes DO
            /* Create the cassette */
            INSERT INTO Components VALUES (NULL, lSequenceID, 0, "CASSETTE", "", "");
            SET lCurrentCassetteID = LAST_INSERT_ID();

            /* Update references to the new cassette */
            IF lCassette = 0 THEN
                /* This is the first cassette.  Update the sequences table */
                UPDATE Sequences SET FirstComponentID = lCurrentCassetteID where SequenceID = lSequenceID;
            ELSE
                /* This is a subsequenct cassette.  Update the previous cassette */
                UPDATE Components SET NextComponentID = lCurrentCassetteID where ComponentID = lPreviousCassetteID;
            END IF;

            /* Start the cassette JSON string */
            SET lCassetteJSON = CONCAT("{\"type\":\"CASSETTE\", \"reactor\":", lCassette + 1, ", \"available\":False, \"reagents\":[");

            /* Create the reagents */
            SET lReagent = 0;
            WHILE lReagent < iReagents DO
                /* Create an entry in the reagents table */
                INSERT INTO Reagents VALUES (NULL, lSequenceID, lCurrentCassetteID, lReagent + 1, False, "", "");
                SET lReagentID = LAST_INSERT_ID();

                /* Update the cassette JSON string */
                IF lReagent = 0 THEN
                    SET lCassetteJSON = CONCAT(lCassetteJSON, lReagentID);
                ELSE
                    SET lCassetteJSON = CONCAT(lCassetteJSON, ", ", lReagentID);
                END IF;

                /* Increment the reagent counter */
                SET lReagent = lReagent + 1;
            END WHILE;

            /* Create the columns */
            SET lColumn = 0; 
            WHILE lColumn < iColumns DO
                /* Create an entry in the reagents table */
                INSERT INTO Reagents VALUES (NULL, lSequenceID, lCurrentCassetteID, CHAR(ASCII('A') + lColumn), False, "", "");
                SET lReagentID = LAST_INSERT_ID();

                /* Update the cassette JSON string */
                SET lCassetteJSON = CONCAT(lCassetteJSON, ", ", lReagentID);

                /* Increment the column counter */
                SET lColumn = lColumn + 1;
            END WHILE;

            /* Finish the cassette JSON string */
            SET lCassetteJSON = CONCAT(lCassetteJSON, "]}");

            /* Update the cassette JSON string */
            UPDATE Components SET Details = lCassetteJSON WHERE ComponentID = lCurrentCassetteID;

            /* Remember the previous cassette and increment the cassette counter */
            SET lPreviousCassetteID = lCurrentCassetteID;
            SET lCassette = lCassette + 1;
        END WHILE;

        /* Set our return value */
        SET oSequenceID = lSequenceID;
    END //

/****************************************************************************************************************************************************************
 ** Reagents ****************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Update an existing reagent:
 *   IN ReagentID - ID of the reagent to update
 *   IN Available - True if a reagent is in this position, False otherwise
 *   IN Name - Reagent name
 *   IN Description - ReagentDescription
 */
CREATE PROCEDURE UpdateReagent(IN iReagentID INT UNSIGNED, IN iAvailable BOOL, IN iName VARCHAR(64), IN iDescription VARCHAR(255))
    BEGIN
        /* Update the reagent */
        UPDATE Reagents SET Available = iAvailable, Name = iName, Description = iDescription WHERE ReagentID = iReagentID;
    END //

/* Update an existing reagent by position:
 *   IN SequenceID - Sequence ID of the reagent to update
 *   IN CassetteNumber - Cassette number of the reagent to update
 *   IN Position - Position of the reagent to update
 *   IN Available - True if a reagent is in this position, False otherwise
 *   IN Name - Reagent name
 *   IN Description - ReagentDescription
 */
CREATE PROCEDURE UpdateReagentByPosition(IN iSequenceID INT UNSIGNED, IN iCassetteNumber INT UNSIGNED, IN iPosition VARCHAR(2), IN iAvailable BOOL,
                               IN iName VARCHAR(64), IN iDescription VARCHAR(255))
    BEGIN
        /* Get the reagent by position */
        DECLARE lReagentID INT UNSIGNED;
        CALL GetReagentByPosition(iSequenceID, iCassetteNumber, iPosition, lReagentID);

        /* Update the reagent */
        CALL UpdateReagent(lReagentID, iAvailable, iName, iDescription);
    END //

/* Gets a reagent by position:
 *   IN SequenceID - Sequence ID of the reagent to update
 *   IN CassetteNumber - Cassette number of the reagent to update
 *   IN Position - Position of the reagent to update
 *   OUT ReagentID - ID of the reagent
 */
CREATE PROCEDURE GetReagentByPosition(IN iSequenceID INT UNSIGNED, IN iCassetteNumber INT UNSIGNED, IN iPosition VARCHAR(2), OUT oReagentID INT UNSIGNED)
    BEGIN
        /* Declare local variables */
        DECLARE lComponentID INT UNSIGNED;

        /* Look up the component ID of the cassette */
        CALL GetComponentByOffset(iSequenceID, iCassetteNumber - 1, lComponentID);

        /* Look up the reagent by position */
        SET oReagentID = (SELECT ReagentID FROM Reagents WHERE SequenceID = iSequenceID AND ComponentID = lComponentID AND Position = iPosition);
    END //

/****************************************************************************************************************************************************************
 ** Components **************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Returns the first component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   OUT ComponentID - ID of the first component in the sequence
 */
CREATE PROCEDURE GetFirstComponent(IN iSequenceID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        /* Get the first component ID */
        SET oComponentID = (SELECT FirstComponentID FROM Sequences WHERE SequenceID = iSequenceID);
    END //

/* Returns the next component of a sequence:
 *   IN ComponentID - ID of the current component
 *   OUT ComponentID - ID of the next component in the sequence
 */
CREATE PROCEDURE GetNextComponent(IN iComponentID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        /* Get the next component ID */
        SET oComponentID = (SELECT NextComponentID FROM Components WHERE ComponentID = iComponentID);
    END //

/* Returns the Nth component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   IN ComponentOffset - Offset of the component
 *   OUT ComponentID - ID of the component
 */
CREATE PROCEDURE GetComponentByOffset(IN iSequenceID INT UNSIGNED, IN iComponentOffset INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        /* Declare local variables */
        DECLARE lComponentID INT UNSIGNED default 0;
        DECLARE lComponentOffset INT UNSIGNED default 0;

        /* Loop until we reach the desired offset */
        WHILE lComponentOffset <= iComponentOffset DO
            IF lComponentOffset = 0 THEN
                /* Get the first component ID */
                CALL GetFirstComponent(iSequenceID, lComponentID);
            ELSE
                /* Get the next component ID */
                CALL GetNextComponent(lComponentID, lComponentID);
            END IF;

            /* Increment the component counter */
            SET lComponentOffset = lComponentOffset + 1;
        END WHILE;

        /* Set the return value */
        SET oComponentID = lComponentID;
    END //

/* Restore the delimiter */
DELIMITER ;

