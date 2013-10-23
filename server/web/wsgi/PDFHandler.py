#!/usr/bin/env python
'''
Added by: Luis
Date: 10/16/2013
Class will handle the PDF generation for
the run sequence screen. Will send a DB
request and obtain the sequence ran.
Will display all components executed during the
run process on a PDF file.
File location: /var/www/http/files
'''
import sys
sys.path.append('/opt/elixys/database')
sys.path.append('/opt/elixys/core')
sys.path.append('/opt/elixys/config')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from DBComm import *
from time import strftime
from datetime import datetime
from collections import Iterable

import logging
log = logging.getLogger("error.log")


class PDFHandler:
  def __init__(self):
    pDatabase = DBComm()
    pDatabase.Connect()   

  def testWrite(self):
    pdf_text = canvas.Canvas("/var/www/http/files/test.pdf")
    pdf_text.drawString(500,300,"THIS IS A TEST!")
    pdf_text.showPage()
    pdf_text.save()
    
  def getSequences(self,pClientState,sRemoteUser,pDatabase):
    '''
    This function will query the DB and
    return all the sequences ran during
    the task executed.    
    '''
    # search the client state and find the sequence id
    sequence = pClientState["sequenceid"] 
    # query the database for the sequence's information and insert in into the title.
    sequence_result_set = pDatabase.GetSequence(sRemoteUser,int(sequence))
    # First, try to create the canvas and set the title of the pdf to
    # the name of the sequence ran and the current date/time.
    try:
        filename = datetime.now().strftime("%Y-%m-%d_%H_%M") + "_" + str(sequence_result_set["metadata"]["name"]).replace(" ","_")
        pdf_text = canvas.Canvas(
            "/var/www/http/files/" +
            filename,
            pagesize=letter)
            
    except Exception as e:
        log.error("Error: Exception " + str(e))
        pdf_text = canvas.Canvas(
            "/var/www/http/files/" +
            "Unkown_test_" +
            datetime.now().strftime("%Y-%m-%d_%H_%M"),
            pagesize=letter)
    
    # Now, we need to querty on all components with the sequence id
    # and pull them.
    component_result_set = pDatabase.GetComponentsBySequence(sRemoteUser,int(sequence))
   
    # Set the header and the line of the text of the page as page height.
    page_height = 745
    page_height = drawHeader(pdf_text,page_height)
    pdf_text.setFont("Helvetica",12)
    
    # Go through each section of the returned query result
    # and add each line to the pdf file.
    # First, loop through all the elements in the result set.
    # Then, loop through each elment's dictionary.
    for components in component_result_set:
        for k,v in components.iteritems():
            if page_height <= 40:
                pdf_text.showPage()
                page_height = 745
            pdf_text.drawString(inch*.2, page_height,
                str(k) + " : " + str(v))
            page_height -= 20
    
    #for k,v in sequence_result_set.iteritems():
    #   
    #    if page_height <= 0:
    #        pdf_text.showPage()
    #        page_height = 745
    #    
    #    if str(k) == "components":
    #        temp = dict(sequence_result_set[k][0]) 
    #        for k2,v2 in temp.iteritems():
    #            if page_height <= 0:
    #                pdf_text.showPage()
    #                page_height = 745
    #            pdf_text.drawString(inch*.2,page_height,str(k2) + " : " + str(v2))
    #            page_height -= 15
    #    else:
    #        temp = ""
    #        try:
    #            temp = dict(v)
    #            for k2,v2 in temp.iteritems():
    #                if page_height <= 0:
    #                    pdf_text.showPage()
    #                    page_height = 745
    #                pdf_text.drawString(inch*.2,page_height,str(k2) + " : " + str(v2))
    #                page_height -= 15
    #        except Exception:
    #          pdf_text.drawString(inch*.2,page_height,str(k) + " : " + str(v))
    #          page_height -= 15
    #
    
    pdf_text.drawString(inch*.2, page_height, str(filename))
        
    pdf_text.showPage()
    pdf_text.save()
    
    # Finally, return the filename of the PDF.
    return filename
    

    
  
def drawHeader(pdf_text,page_height):
    '''Function will draw the header of the batch record pdf.
    Header contains the title and the date created.
    '''
    #display the title of the document and time created.
    pdf_text.setFont("Helvetica",18)
    pdf_text.drawString(inch*3,page_height," Batch Record")
    page_height-=20
    pdf_text.drawString(inch*3,page_height,
        str(datetime.now().strftime("%l:%M%p - %m/%d/%Y")))
    page_height-=20
    
    return page_height