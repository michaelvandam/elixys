"""Messaging

Elixys Messaging
"""

from MessagingThread import *

# Messaging class
class Messaging:
  def __init__(self, sUsername, pDatabase):
    """Constructor"""
    # Initialize messaging variables
    self.username = sUsername
    self.database = pDatabase

    # Create list of emails and phone numbers
    pAllUsers = pDatabase.GetAllUsers(sUsername)
    self.emailAddresses = []
    self.phoneNumbers = []
    for pUser in pAllUsers:
        if pUser["email"] != "":
            self.emailAddresses.append(pUser["email"])
        if pUser["phone"] != "":
            self.phoneNumbers.append(pUser["phone"])

  def broadcastMessage(self, sMessage):
    """Broadcasts a message"""
    pMessagingThread = MessagingThread()
    pMessagingThread.SetParameters(self.username, self.database, self.emailAddresses, \
      self.phoneNumbers, sMessage)
    pMessagingThread.setDaemon(True)
    pMessagingThread.start()

