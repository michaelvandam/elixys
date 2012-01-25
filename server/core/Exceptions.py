"""Exceptions

Elixys exceptions
"""

# Sequence not found exception
class SequenceNotFoundException(Exception):
    def __init__(self, nSequenceID):
        self.nSequenceID = nSequenceID
    def __str__(self):
        return ("Sequence " +  str(self.nSequenceID) + " not found")

# Component not found exception
class ComponentNotFoundException(Exception):
    def __init__(self, nComponentID):
        self.nComponentID = nComponentID
    def __str__(self):
        return ("Component " +  str(self.nComponentID) + " not found")

# Reagent not found exception
class ReagentNotFoundException(Exception):
    def __init__(self, nReagentID, nSequenceID = 0, nCassette = 0, sPosition = ""):
        self.nReagentID = nReagentID
        self.nSequenceID = nSequenceID
        self.nCassette = nCassette
        self.sPosition = sPosition

    def __str__(self):
        if self.nReagentID != 0:
            return ("Reagent " +  str(self.nReagentID) + " not found")
        else:
            return ("Failed to get reagent " + self.sPosition + " of sequence " + str(self.nSequenceID) + ", cassette " + str(self.nCassette))
# Invalid sequence exception
class InvalidSequenceException(Exception):
    def __init__(self, nSequenceID):
        self.nSequenceID = nSequenceID
    def __str__(self):
        return ("Invalid sequence: " + str(self.nSequenceID))

# State misalignment exception
class StateMisalignmentException(Exception):
    def __str__(self):
        return ("State misalignment")

