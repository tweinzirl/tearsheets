from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def get_mail_server(server='smtp.gmail.com', port=587):
    '''Allocate mail server on port'''
    mailServer = smtplib.SMTP(server, port)
    test = mailServer.starttls()  # start TLS
    mailServer.login(os.environ['GMAIL_ADDRESS'], os.environ['GMAIL_PS'])
    assert test[1].lower().find(b'ready') != -1
    return mailServer


def format_message(message, sender, receiver, subject, attachment_dir='data/tearsheets'):
    '''
    Format arguments into MIMEMultipart object
    '''
    # message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ', '.join(receiver)
    msg['Subject'] = subject

    # gen cid and update text and generate cid or any images
    html_img = re.findall('img src="([a-zA-Z/\.]+)"', message)
    for i, hi in enumerate(html_img):
        # read image and make header for image
        with open(os.path.join(attachment_dir, hi), 'rb') as fp:
            msgImage = MIMEImage(fp.read())
        
        # attach header and assign cid
        msgImage.add_header('Content-ID', f'<image{i}>')
        msg.attach(msgImage)

        # rename in original message
        message = message.replace(hi, f'cid:image{i}')

    #print(message)

    # finally attach original html after images are renamed
    msg.attach(MIMEText(message, 'html'))

    return msg


#def send_message(order_summary, email):
def send_message(message, subject, receiver, sender='TearsheetChatbot.com', attachment_dir='data/tearsheets', verbose=True):
    """
    Send the tearsheet to the intended recipient address. Any images in the html
    are converted to Content-IDs and renamed in the html. All embedded images
    must live in the `attachment_dir` directory for this to work.
    """

    # deal with attachments here
    msg = format_message(message, sender, [receiver], subject, attachment_dir)
    
    if verbose:
        print(f'sending mail from {sender} to {receiver}')
        print(msg)
    with get_mail_server() as mailServer:
        mailServer.sendmail(sender, receiver, msg.as_string())
        
    return msg, 'mail sent successfully'
