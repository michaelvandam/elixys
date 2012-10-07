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
    self.systemConfiguration = pDatabase.GetConfiguration(sUsername)
    self.twilioClient = None
    if (self.systemConfiguration["twilioaccount"] != "") and (self.systemConfiguration["twiliotoken"] != "") and \
        (self.systemConfiguration["twiliofromphone"] != ""):
      self.twilioClient = TwilioRestClient(self.systemConfiguration["twilioaccount"], self.systemConfiguration["twiliotoken"])

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
      self.twilioClient.sms.messages.create(to=sPhoneNumber, from_=self.systemConfiguration["twiliofromphone"], body=sMessage)

