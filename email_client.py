import imaplib
import email
from email.header import decode_header
import sys
import time
import datetime
from dataclasses import dataclass

@dataclass
class StructuredInput:
    uids: str                    # unikatni id
    sender_address: str           # od koho
    subject: str                  # předmět
    body: str                     # text zprávy
    date_of_inbound: str          # datum ve formátu YYYY-MM-DDThh:mm
    non_generic_files: bool       # True = .pdf/.doc atd., False = png/jpg
    processed: bool               # byl jiz zpracovan a zapsan true-projel LLM, false nic se snim nedelo

    def __post_init__(self):
        # ověření formátu datumu
        try:
            datetime.strptime(self.date_of_inbound, "%Y-%m-%dT%H:%M")
        except ValueError:
            raise ValueError(f"date_of_inbound musí být ve formátu YYYY-MM-DDThh:mm, dostal: {self.date_of_inbound}")
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
        return (f"Adresa odesílatele: {self.sender_address}\nPředmět: {self.subject}\nText: {self.body}")

    def to_text_autoreponce(self):
        return (f"Adresa odesílatele: {self.sender_address}\nPředmět: {self.subject}\nText: {self.body}\nDatum doručení: {self.date_of_inbound}\nPřílohy: {self.non_generic_files}")

    def to_text_full(self):
        return (f"ID: {self.uids}\nAdresa odesílatele: {self.sender_address}\nPředmět: {self.subject}\nText: {self.body}\nDatum doručení: {self.date_of_inbound}\nPřílohy: {self.non_generic_files}\nZpracováno: {self.processed}")


####################################################################


from datetime import datetime
import imaplib
import email
from email.header import decode_header

#[b'1 (UID 12)']
extract_uid = lambda x: x[0].decode('utf-8').split("UID ")[1].split(")")[0].strip(")'] ")

def read_inbox(email_imap_server, email_SSL_port, email_user, email_pass, email_folder):
    """
    Return list of StructuredInput objects for all emails in folder.
    UID is returned as raw string for direct server lookup.
    """
    emails = []
    try:
        mail = imaplib.IMAP4_SSL(email_imap_server, email_SSL_port, timeout=30)
        mail.login(email_user, email_pass)
        mail.select(email_folder)

        status, message_numbers = mail.search(None, "ALL")
        if status != 'OK':
            print("Chyba při získávání seznamu zpráv.")
            return emails

        for num in message_numbers[0].split():
            # 1. Získání UID z odpovědi serveru
            status, uid_data = mail.fetch(num, "(UID)")
            if status == 'OK':
                    msg_uid= extract_uid(uid_data)

            # Získání celé zprávy (pokud ještě nebylo)
            if 'msg_data' not in locals():
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
            date_str = msg.get("Date", "")
            try:
                dt = email.utils.parsedate_to_datetime(date_str)
                date_of_inbound = dt.strftime("%Y-%m-%dT%H:%M")
            except:
                date_of_inbound = ""

            # Body (plain text)
            body = ""
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
                uids=msg_uid,
                sender_address=sender,
                subject=subject,
                body=body,
                date_of_inbound=date_of_inbound,
                non_generic_files=non_generic_files,
                processed=False
            ))

        mail.logout()
        print("Konec načítání zpráv.")
        return emails

    except Exception as e:
        print(f"Chyba:\n{str(e)}")
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
    emails= read_inbox("imap.seznam.cz", "993", "ete-test@email.cz", "SJy,nht3c0*CiIqz8TSffHg0Tk*aJnnI#H","inbox")
    for em in emails:
        print(em.to_text_full())


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