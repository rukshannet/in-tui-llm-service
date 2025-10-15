import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

def send_gmail(user_email: str, subject: str, body: str) -> None:
    """
    Sends an email using the Gmail SMTP server.

    NOTE: For security, use a Google "App Password" instead of your main 
          Gmail account password, as standard password authentication 
          is often blocked by Google.

    Args:
        sender_email: The sender's Gmail address (e.g., 'your.email@gmail.com').
        sender_password: The sender's App Password for Gmail.
        receiver_email: The recipient's email address.
        subject: The subject line of the email.
        body: The plain text content of the email.
    """
    
    SENDER_EMAIL = "intuimail@gmail.com" 
    APP_PASSWORD = "fxxp sjmp ekqd hbod" 
    RECEIVER_EMAIL = ["me@rukshan.net", user_email]  # Support team email and CC to user

    # Configuration for Gmail's SMTP server
    smtp_server = "smtp.gmail.com"
    port = 587  # StartTLS port

    # Create the base message container
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] =  "support@in-tui.com"
    message["Cc"] = ", ".join(RECEIVER_EMAIL)  # CC the sender

    # Attach the plain text body to the message
    text_part = MIMEText(body, "plain")
    message.attach(text_part)

    # Create a secure SSL context (required for modern email clients)
    context = ssl.create_default_context()

    try:
        # Connect to the SMTP server using a context manager
        # The connection starts in plain mode and is upgraded to secure via STARTTLS
        with smtplib.SMTP(smtp_server, port) as server:
            # 1. Start TLS encryption
            server.starttls(context=context) 
            
            # 2. Log in to the email account
            server.login(SENDER_EMAIL, APP_PASSWORD)
            
            # 3. Send the email
            server.sendmail(
                SENDER_EMAIL, [user_email] + RECEIVER_EMAIL, message.as_string()
            )
            
        print(f"Successfully sent email to {user_email}")

    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP Authentication Failed.")
        print("Please check if the sender_email and sender_password (App Password) are correct.")
        print("Also ensure 'Less Secure App Access' is not required or that an App Password is used.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

        
