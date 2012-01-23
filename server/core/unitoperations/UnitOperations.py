"""Unit operations
Elixys Unit Operations
"""

# Import unit operations
import Cassette
import Add
import Evaporate
import Transfer
import React
import Prompt
import Install
import Comment
import TrapF18
import EluteF18
import Initialize
import Mix
import Move
import Summary
import ExternalAdd

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel = None):
  if pComponent["componenttype"] == Cassette.componentType:
    return Cassette.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Add.componentType:
    return Add.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Evaporate.componentType:
    return Evaporate.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Transfer.componentType:
    return Transfer.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == React.componentType:
    return React.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Prompt.componentType:
    return Prompt.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Install.componentType:
    return Install.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Comment.componentType:
    return Comment.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == TrapF18.componentType:
    return TrapF18.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == EluteF18.componentType:
    return EluteF18.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Initialize.componentType:
    return Initialize.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Mix.componentType:
    return Mix.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Move.componentType:
    return Move.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Summary.componentType:
    return Summary.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == ExternalAdd.componentType:
    return ExternalAdd.createFromComponent(nSequenceID, pComponent, username, database, systemModel)
  else:
    raise Exception("Unknown component type: " + pComponent["componenttype"])

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel = None):
  if pComponent["componenttype"] == Cassette.componentType:
    return Cassette.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Add.componentType:
    return Add.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Evaporate.componentType:
    return Evaporate.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Transfer.componentType:
    return Transfer.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == React.componentType:
    return React.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Prompt.componentType:
    return Prompt.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Install.componentType:
    return Install.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Comment.componentType:
    return Comment.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == TrapF18.componentType:
    return TrapF18.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == EluteF18.componentType:
    return EluteF18.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Initialize.componentType:
    return Initialize.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Mix.componentType:
    return Mix.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Move.componentType:
    return Move.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == Summary.componentType:
    return Summary.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  elif pComponent["componenttype"] == ExternalAdd.componentType:
    return ExternalAdd.updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel)
  else:
    raise Exception("Unknown component type: " + pComponent["componenttype"])

