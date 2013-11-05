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
from datetime import datetime

class PDFHandler:
    '''The PDFHandler class generates the actual
    PDF File. The write_pdf function generates
    the majority of the PDF File and the body
    of the PDF.
    '''
    def __init__(self):
        '''Empty Constructor, No attributes.'''
        pass


    def write_pdf(self, client_state, remote_user, database):
        '''
        This function will query the DB and
        return all the sequences ran during
        the task executed.
        '''
        # Search the client state and find the sequence id
        sequence = int(client_state["sequenceid"])
        # Query the database for the sequence's 
        # information and insert in into the title.
        sequence_result_set = database.GetSequence(
                                        remote_user, 
                                        sequence)
        # First, try to create the canvas and set the title of the pdf to
        # the name of the sequence ran and the current date/time.
        try:
            sequence_result_set = sequence_result_set["metadata"]["name"]
            sequence_name = sequence_result_set
            sequence_result_set = str(sequence_result_set).replace(" ","_")

            filename = (datetime.now().strftime("%Y-%m-%d_%H_%M") + 
                        "_" + sequence_result_set)
            pdf_text = canvas.Canvas(
                "/var/www/http/files/" +
                filename,
                pagesize=letter)

        except ValueError:
            filename = "Unkown_test_"
            sequence_name = "Unkown"
            pdf_text = canvas.Canvas(
                        "/var/www/http/files/" +
                        filename +
                        datetime.now().strftime("%Y-%m-%d_%H_%M"),
                        pagesize=letter)

        # Now, we need to querty on all components with the sequence id
        # and pull them.
        component_result_set = database.GetComponentsBySequence(
                                remote_user,
                                sequence)

        # Set the header and the line of the text of the page as page height.
        page_height = 740
        draw_logo(pdf_text, page_height) 
        page_height = draw_header(pdf_text, page_height, sequence_name)
 
        pdf_text.setFont("Helvetica", 12)
        # Set the Main information panel. This panel contains information
        # regarding sequence name, comment, creation date and user.
        
        page_height = draw_main_panel(pdf_text, page_height,
                                    remote_user, sequence, database)

        
        pdf_text.setFont("Helvetica", 12)

        # Go through each section of the returned query result
        # and add each line to the pdf file.
        # First, loop through all the elements in the result set.
        # Then, loop through each elment's dictionary.
        for components in component_result_set:
            for key, value in components.iteritems():
                if page_height <= 40:
                    pdf_text.showPage()
                    page_height = 745
                # If we hit another component, start a new section.    
                if key == "componenttype":
                    # Check if the section should be displayed on the next page.
                    if page_height < 100:
                        pdf_text.showPage()
                        page_height = 745
                        page_height = draw_section_line(pdf_text, page_height)
                        pdf_text.setFont("Helvetica", 14)
                        pdf_text.drawString(inch*.2, page_height, str(value))
                        pdf_text.setFont("Helvetica", 12)
                        page_height -= 20
                    else:
                        page_height = draw_section_line(pdf_text, page_height)
                        pdf_text.setFont("Helvetica", 14)
                        pdf_text.drawString(inch*.2, page_height, str(value))
                        pdf_text.setFont("Helvetica", 12)
                        page_height -= 20
                
                else:
                    pdf_text.drawString(inch*.2, page_height,
                        str(key) + " : " + str(value))
                    page_height -= 20


        pdf_text.showPage()
        pdf_text.save()

        # Finally, return the filename of the PDF.
        return filename


def draw_header(pdf_text, page_height, sequence_name):
    '''Function will draw the header of the batch record pdf.
    Header contains the title and the date created.
    '''
    #display the title of the document and time created.
    pdf_text.setFont("Helvetica", 18)
    pdf_text.drawString(inch*3, page_height, " Batch Record - " + sequence_name)
    page_height -= 20
    pdf_text.drawString(inch*3, page_height,
        str(datetime.now().strftime("%l:%M%p - %m/%d/%Y")))
    page_height -= 20

    return page_height

def draw_logo(pdf_text, page_height):
    '''Function will draw the sofiebio logo onto the pdd.
    The location of the image is located in /var/www/http/images
    '''
    sofie_logo_path = '/var/www/http/images/sofie_blue.jpg'
    width, height = letter
    pdf_text.drawImage(sofie_logo_path, inch*.2, page_height, 180, 30)

def draw_section_line(pdf_text, page_height):
    '''Function will draw a line to divid up sections for each
    component type.
    '''
    pdf_text.line(inch*.2,page_height,inch*8,page_height)
    page_height -= 15

    return page_height

def draw_main_panel(pdf_text, page_height, remote_user ,sequence, database):
    '''Function will draw the the main information panel.
    This panel shall contain information on the sequence
    name, comment, creation date and user name.
    '''
    # Draw the Header of the panel.
    main_panel = "Main Sequence Information"
    pdf_text.setFont("Helvetica", 14)
    pdf_text.drawString(inch*.2, page_height, main_panel)
    page_height -= 20
    
    pdf_text.setFont("Helvetica", 12)

    sequence_data = database.GetSequence(remote_user, sequence)
    
    # Traverse through the sequence data and write to page.
    # Obtain the metadata that contains information about the sequence.
    # If statements to show only useful information.
    for key, value in sequence_data.iteritems():
        if page_height <= 40:
            pdf_text.showPage()
            page_height = 745
        if key == 'metadata':
            for key2, value2 in value.iteritems():
                if (key2 == 'comment' or key2 == 'name' or key2 == 'creator'
                        or key2 == 'timestamp' or key2 == 'components'):
                    pdf_text.drawString(inch*.2, page_height,
                        str(key2) + " : " + str(value2))
                    page_height -= 20
    return page_height
 
