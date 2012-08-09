"""Messaging

Elixys Messaging
"""

from twilio.rest import TwilioRestClient

# Messaging class
class Messaging:
  def __init__(self, sUsername, pDatabase):
    """Constructor"""
    # Initialize messaging variables
    self.username = sUsername
    self.database = pDatabase
    self.systemConfiguration = pDatabase.GetConfiguration(sUsername)
    self.twilioClient = None
    if (self.systemConfiguration["twilioaccount"] != "") and (self.systemConfiguration["twiliotoken"] != "") and \
        (self.systemConfiguration["twiliofromphone"] != ""):
      self.twilioClient = TwilioRestClient(self.systemConfiguration["twilioaccount"], self.systemConfiguration["twiliotoken"])

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
    for sEmail in self.emailAddresses:
      self.emailMessage(sMessage, sEmail)
    for sPhone in self.phoneNumbers:
      self.smsMessage(sMessage, sPhone)

  def emailMessage(self, sMessage, sEmailAddress):
    """Sends an email to the address"""
    print "### Send email to: " + sEmailAddress

  def smsMessage(self, sMessage, sPhoneNumber):
    """Send an SMS to the phone number"""
    if self.twilioClient != None:
      self.twilioClient.sms.messages.create(to=sPhoneNumber, from_=self.systemConfiguration["twiliofromphone"], body=sMessage)

