import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from settings import MY_ADDRESS, PASSWORD, DB_FILE_LOCATION, RECIPIENT_EMAILS

def get_contacts(RECIPIENT_EMAILS):
    """
    Return two lists names, emails containing names and email addresses
    read from our RECIPIENT_EMAILS
    """

    names = []
    emails = []
    for contacts in RECIPIENT_EMAILS:
        names.append(contacts.split()[0])
        emails.append(contacts.split()[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """
    
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def main():
    names, emails = get_contacts(RECIPIENT_EMAILS) # read contacts
    message_template = read_template('emailBody.txt')

    # set up the SMTP server
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())

        num_jobs = message.count('\n')

        # setup the parameters of the message
        msg['From']=MY_ADDRESS
        msg['To']=email
        if num_jobs == 0:
            msg['Subject']="No new jobs found today"
        if num_jobs == 1:
            msg['Subject']="1 new job found today"
        else:
            msg['Subject']="{0} new jobs have been found!".format(num_jobs)
        
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))
############################################################################################################
# Attach the updated SQLite.db with the email
        # open the file to be sent  
        filename = "JobScraper_DB.db"
        # AWS attachment
        # attachment = open(r"/home/ec2-user/JobScraper_DB.db", "rb")
        
        # PC attachment
        attachment = open(DB_FILE_LOCATION, "rb") 
        
        # instance of MIMEBase and named as p 
        p = MIMEBase('application', 'octet-stream') 
        
        # To change the payload into encoded form 
        p.set_payload((attachment).read()) 
        
        # encode into base64 
        encoders.encode_base64(p) 
        
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
############################################################################################################       
        # attach the instance 'p' to instance 'msg' 
        msg.attach(p)
        
        # send the message via the server set up earlier.
        s.send_message(msg)
        del msg
        
    # Terminate the SMTP session and close the connection
    s.quit()
    
if __name__ == '__main__':
    main()