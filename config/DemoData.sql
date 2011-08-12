/* Create the user roles */
SET @RoleID = 0;
CALL CreateNewRole("Administrator", 255, @RoleID);
CALL CreateNewRole("Researcher", 255, @RoleID);
CALL CreateNewRole("Technician", 255, @RoleID);

/* Create the users */
SET @UserID = 0;
CALL CreateNewUser("Administrator", "6E3kYsJnM9p2Y", "first", "last", "Administrator", @UserID);
CALL CreateNewUser("Researcher", "6E3kYsJnM9p2Y", "first", "last", "Researcher", @UserID);
CALL CreateNewUser("Technician", "6E3kYsJnM9p2Y", "first", "last", "Technician", @UserID);
CALL CreateNewUser("devel", "6E3kYsJnM9p2Y", "first", "last", "Administrator", @UserID);
CALL CreateNewUser("shane", "6E3kYsJnM9p2Y", "Shane", "Claggett", "Administrator", @UserID);
CALL CreateNewUser("kevin", "6E3kYsJnM9p2Y", "Kevin", "Quinn", "Administrator", @UserID);
CALL CreateNewUser("mike", "6E3kYsJnM9p2Y", "Mike", "van Dam", "Administrator", @UserID);
CALL CreateNewUser("melissa", "6E3kYsJnM9p2Y", "Melissa", "Esterby", "Administrator", @UserID);
CALL CreateNewUser("jeff", "6E3kYsJnM9p2Y", "Jeff", "Esterby", "Administrator", @UserID);
CALL CreateNewUser("mark", "6E3kYsJnM9p2Y", "Mark", "Lazari", "Researcher", @UserID);
CALL CreateNewUser("garauv", "6E3kYsJnM9p2Y", "Gaurav", "Shah", "Researcher", @UserID);
CALL CreateNewUser("graciela", "6E3kYsJnM9p2Y", "Graciela", "Flores", "Researcher", @UserID);
CALL CreateNewUser("patrick", "6E3kYsJnM9p2Y", "Patrick", "Phelps", "Researcher", @UserID);

/* Create the FAC synthesis sequence */
SET @SequenceID = 0;
CALL CreateNewSequence("FAC Synthesis", "Sequence for the synthesis of FAC", "devel", 3, 10, 2, @SequenceID);

/* Fill in the sequence reagents by position */
CALL UpdateReagentByPosition(@SequenceID, 1, "1", True, "K222", "Kryptofix and potassium carbonate in acetonitrile");
CALL UpdateReagentByPosition(@SequenceID, 1, "2", True, "MeCN1", "acetonitrile");
CALL UpdateReagentByPosition(@SequenceID, 1, "3", True, "MeCN2", "acetonitrile");
CALL UpdateReagentByPosition(@SequenceID, 1, "4", True, "Precursor1", "tribenzoyl pentose triflate in acetonitrile");
CALL UpdateReagentByPosition(@SequenceID, 1, "A", True, "QMA", "QMA column");

/* Create the sequence unit operations */

