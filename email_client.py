import imaplib
import email
from email.header import decode_header
import datetime
from dataclasses import dataclass
import imaplib


@dataclass
class StructuredInput:
    uids: str                    # unikatni id
    sender_address: str           # od koho
    subject: str                  # předmět
    body: str                     # text zprávy
    date_of_inbound: str          # datum ve formátu YYYY-MM-DDThh:mm
    non_generic_files: bool       # True = .pdf/.doc atd., False = png/jpg
    processed: bool               # byl jiz zpracovan a zapsan true-projel LLM, false nic se snim nedelo


    def __str__(self) -> str:
        return (
        f"UID: {self.uids}\n"
        f"Adresa odesílatele: {self.sender_address}\n"
        f"Předmět: {self.subject}\n"
        f"Text: {self.body}\n"
        f"Datum přijetí: {self.date_of_inbound}\n"
        f"Non-generic files: {self.non_generic_files}\n"
        f"Processed: {self.processed}"
        )


    def to_text_calendar(self):
        return f"Adresa odesílatele: {self.sender_address.replace('\r\n','\n').replace('\n','')}\nPředmět: {self.subject.replace('\r\n','\n').replace('\n','')}\nText: {self.body.replace('\r\n','\n').replace('\n','')}"

    def to_text_autoreponce(self):
        return f"Adresa odesílatele: {self.sender_address.replace('\r\n','\n')}\nPředmět: {self.subject.replace('\r\n','\n')}\nText: {self.body.replace('\r\n','\n')}\nDatum doručení: {self.date_of_inbound}\nPřílohy: {self.non_generic_files}"
    
    def to_text_full(self):
        return f"ID: {self.uids}\nAdresa odesílatele: {self.sender_address.replace('\r\n','\n')}\nPředmět: {self.subject.replace('\r\n','\n')}\nText: {self.body.replace('\r\n','\n')}\nDatum doručení: {self.date_of_inbound}\nPřílohy: {self.non_generic_files}\nZpracováno: {self.processed}"

####################################################################




#[b'1 (UID 12)']
extract_uid = lambda x: x[0].decode('utf-8').split("UID ")[1].split(")")[0].strip(")'] ")

def read_inbox(email_imap_server, email_SSL_port, email_user, email_pass, email_folder):
        """
    Return list of StructuredInput objects for all emails in folder.
    UID is returned as raw string for direct server lookup.
        """
        emails = []
    
        mail = imaplib.IMAP4_SSL(email_imap_server, email_SSL_port, timeout=30)
        mail.login(email_user, email_pass)
        mail.select(email_folder)

        blob = mail.search(None, "ALL")
        if blob[0] != 'OK':
            print("Chyba při získávání seznamu zpráv.")
            return emails
        
        serial_number=blob[1][0].decode().replace("']","").replace("[b'","")
        for num in serial_number.split(" "):

            msg: vars
            msg = None
            uid = ""
            sender=""
            subject = ""
            body = ""
            date_of_inbound=""
            non_generic_files = False
            procesed = False

            # 1. Získání UID z odpovědi serveru
            status, uid_data = mail.fetch(num, "(UID)")
            if status == 'OK':
                uid = extract_uid(uid_data)
                status, msg_data = mail.fetch(num, "(RFC822)")
                if status != 'OK':
                    continue
                msg = email.message_from_bytes(msg_data[0][1])

            # Sender
            sender = msg.get("From", "")
            # Subject
            subject, encoding = decode_header(msg.get("Subject", ""))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            # Date
            try:
                date_of_inbound = email.utils.parsedate_to_datetime(msg.get("Date", "")).strftime("%Y-%m-%dT%H:%M") 
            except:
                date_of_inbound = "0000-00-00T00:00"

            # Body (plain text)           
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    disp = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in disp:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            # Kontrola příloh
            non_generic_files = False
            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename()
                    if filename:
                        ext = filename.split(".")[-1].lower()
                        if ext in ["pdf", "doc", "docx", "xlsx", "pptx"]:
                            non_generic_files = True
                            break

            # Přidání do seznamu
            emails.append(StructuredInput(
                uids=uid,
                sender_address=sender,
                subject=subject,
                body=body,
                date_of_inbound=date_of_inbound,
                non_generic_files=non_generic_files,
                processed=procesed
            ))
      

        mail.logout()
        print("Konec načítání zpráv.")
        return emails


#########################################################################################


def delete_processed_emails_in_folder(email_imap_server, email_SSL_port, email_user, email_pass, email_folder, emails):#warning - this function is ganerated by AI
    """
    Smaže všechny emaily, jejichž processed = True.
    email_objects: list of StructuredInput
    """
    try:
        # Připojení k IMAP serveru
        mail = imaplib.IMAP4_SSL(email_imap_server, email_SSL_port, timeout=30)
        mail.login(email_user, email_pass)
        mail.select(email_folder)

        # Procházení zpracovaných emailů
        for email_obj in emails:
            mail.uid('STORE', email_obj.uids, '+FLAGS', r'(\Deleted)')


        # Potvrzení smazání
        mail.expunge()
        mail.logout()
        print("Všechny zpracované emaily byly smazány.")
    except Exception as e:
        print(f"Chyba při mazání emailů:\n{str(e)}")


######################################################################################
#   TEST functions - be careful


def test_read():
    """
    only read all emails and print them as structured output by class StructuredInput by .to_text_full()
    """
    emails= read_inbox("imap.seznam.cz", "993", "ete-test@email.cz", "password","test")
    for em in emails:
        print(em.to_text_full())
        print("-----------------------------------------------------------------------------------------------------")
        print("-----------------------------------------------------------------------------------------------------")

def test_full():
    """
    read all emails, and print them.
    After that it try remove emails.

    REMOVE IS PERNAMENT - NO TRASH/RECYCLE BIN just pernamently remove all emails in the folder! 
    Not use in your production folder, especialy inbox. 
    It is dangerous for you and may have serius consequences.

    """
    emails = read_inbox("imap.seznam.cz", "993", "ete-test@email.cz", "password", "test")
    
    # Vypíšeme e-maily do konzole
    i=0
    for em in emails:
        print(em.to_text_full())
        # Označíme e-maily jako zpracované
        emails[i].processed = True
        i=i+1

    print("-----------------------------------------------------------------------------------------------------")
    print("-----------------------------------------------------------------------------------------------------")

    for em in emails:
        print(em.to_text_full())

    # Spustíme mazání zpracovaných e-mailů
    delete_processed_emails_in_folder("imap.seznam.cz", "993", "ete-test@email.cz", "password", "test", emails)
    
# Spuštění testu
#test_full()
#test_read()