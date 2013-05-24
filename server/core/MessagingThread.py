""" MessagingThread.py

Messaging thread class spawned by Messaging """

### Imports
import threading
import time
from twilio.rest import TwilioRestClient

class MessagingThread(threading.Thread):
  def SetParameters(self, sUsername, pDatabase, pEmailAddresses, pPhoneNumbers, sMessage):
    """Set thread parameters"""
    # Remember the parameters
    self.username = sUsername
    self.database = pDatabase
    self.emailAddresses = pEmailAddresses
    self.phoneNumbers = pPhoneNumbers
    self.message = sMessage

    # Initialize SMS
    self.twilioConfiguration = pDatabase.GetTwilioConfiguration(sUsername)
    self.twilioClient = None
    if (self.twilioConfiguration["account"] != "") and (self.twilioConfiguration["token"] != "") and \
        (self.twilioConfiguration["fromphone"] != ""):
      self.twilioClient = TwilioRestClient(self.twilioConfiguration["account"], self.twilioConfiguration["token"])

  def run(self):
    """Main thread function"""
    try:
      # Send emails and SMS
      for sEmail in self.emailAddresses:
        self.emailMessage(self.message, sEmail)
      for sPhone in self.phoneNumbers:
        self.smsMessage(self.message, sPhone)
    except Exception as ex:
      print "Exception in messaging thread: " + str(ex)

  def emailMessage(self, sMessage, sEmailAddress):
    """Sends an email to the address"""
    pass

  def smsMessage(self, sMessage, sPhoneNumber):
    """Send an SMS to the phone number"""
    if self.twilioClient != None:
      self.twilioClient.sms.messages.create(to=sPhoneNumber, from_=self.twilioConfiguration["fromphone"], body=sMessage)

