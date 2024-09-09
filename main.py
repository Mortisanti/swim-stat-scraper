#region Modules
import base64
import csv
import mimetypes
import os.path
# import pandas as pd
# import pdfkit
import requests
import sqlite3
from csv2pdf import convert
# from openpyxl import Workbook
# from openpyxl.styles import PatternFill, Border, Side
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from data_structures import swimmer_table
from constants import *
#endregion

def main():
    
    #region Initializing webdriver
    def initialize_webdriver():
        browser_options = webdriver.ChromeOptions()
        # Suppress any console message from either the Selenium driver or the browser itself as to run completely silent
        browser_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Attempt to hide certificate errors in the console, which are negligible anyway
        browser_options.add_argument('--ignore-certificate-errors')
        # Headless mode to prevent a visible browser window from opening
        browser_options.add_argument('--headless=new')
        return webdriver.Chrome(options=browser_options)
    #endregion
    
    #region Initializing database
    def initialize_db():
        # Connect to the SQLite db - create a new file if it doesn't exist
        # Create/replace the "swimmers" and "best_times" tables
        connection = sqlite3.connect('swimming_data.db')
        cursor = connection.cursor()
        cursor.execute(f"""DROP TABLE IF EXISTS {TABLE_NAME_SWIMMERS};""")
        cursor.execute(SQL_CREATE_SWIMMERS_TABLE)
        cursor.execute(f"""DROP TABLE IF EXISTS {TABLE_NAME_BEST_TIMES};""")
        cursor.execute(SQL_CREATE_BEST_TIMES_TABLE)
        return connection, cursor
    #endregion

    #region Scraping and storing data
    def scrape_swimmer_info_and_store_data():
        # Find and extract swimmer's full name and age, and insert a record into the swimmers table
        full_name = driver.find_element(By.XPATH, NAME_XPATH).text
        current_age = driver.find_element(By.XPATH, AGE_XPATH).text
        birthdate = swimmer['birthdate']
        try:
            current_age = current_age.split()[-1]
        except IndexError:
            current_age = "N/A"
            print("Failed to retrieve age value.")
            print("Continuing.")
        # Insert into db
        cursor.execute(f"""
                       INSERT INTO {TABLE_NAME_SWIMMERS} (full_name, current_age, birthdate)
                       VALUES('{full_name}', '{current_age}', '{birthdate}');
                       """
        )
        # Add to table row for CSV file
        swimmer_table[0].extend(['', full_name, f'Age: {current_age}', f'DOB: {birthdate}'])
        swimmer_table[1].extend(['', '', 'Actuals', ''])
        swimmer_table[2].extend(['', 'Time', 'Date', 'Standard'])

    def scrape_table_and_store_data(event_category: str):
        best_times_table = driver.find_element(By.XPATH, TABLE_XPATH)
        rows = best_times_table.find_elements(By.TAG_NAME, 'tr')
        event_rows_filled = []
        # Skip the header row and obtain data from the remaining cells
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            cell_texts = [cell.text for cell in cells]
            event, best_time, standard, points, age, meet, meet_date = cell_texts
            # Insert into db
            cursor.execute(f"""
                           INSERT INTO {TABLE_NAME_BEST_TIMES} (swimmer_id, event, best_time, standard, points, age, meet, meet_date)
                           VALUES({swimmer_id}, '{event}', '{best_time}', '{standard}', '{points}', '{age}', '{meet}', '{meet_date}');
                           """
            )
            
            # Quick fix for blank fill bug I encountered.
            # This is not ideal because if any new event types are added to the swimmer_table the starting_element would need to change.
            # TODO: Devise a better solution.
            starting_element = 3
            if event_category == 'LCM':
                starting_element = 25
            
            # Add to swimmer_table to be used for CSV file
            for row in swimmer_table[starting_element:]:
                cell_event = row[0]
                if cell_event == '':
                    continue
                elif cell_event == event:
                    row.extend(['', best_time, meet_date, standard])
                    event_rows_filled.append(event)
                    break
                elif cell_event not in event_rows_filled:
                    row.extend(['', '', '', ''])
                    event_rows_filled.append(cell_event)
    #endregion

    #region Building files
    def build_csv():
        with open(CSV_OUTPUT, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerows(swimmer_table)

    def convert_csv_to_pdf():
        convert(CSV_OUTPUT, CSV_TO_PDF_OUTPUT, orientation='L', size=6)

    # # Optional: Below functions can be used to create a spreadsheet and convert it to HTML and then PDF.
    # # This route could make for a more visually appealing output with more time and effort.
    # def build_xlsx():
    #     wb = Workbook()
    #     ws = wb.active
    #     for row_idx, row_data in enumerate(swimmer_table, start=1):
    #         for col_idx, value in enumerate(row_data, start=1):
    #             ws.cell(row=row_idx, column=col_idx, value=value)
    #     wb.save(XLSX_OUTPUT)

    # def convert_xlsx_to_pdf():
    #         dataframe = pd.read_excel(XLSX_OUTPUT)
    #         pd.options.display.html.border = 0
    #         dataframe.to_html(HTML_OUTPUT, na_rep='')
    #         pdfkit.from_file(HTML_OUTPUT, HTML_TO_PDF_OUTPUT)

    #endregion
    
    #region Authenticating Gmail
    def authenticate_gmail():
        creds = None
        # Check for existence of token file - which stores access and refresh tokens - generated by quickstart.py.
        # Attempt to retrieve auth credentials and store in creds variable.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # Check for existence and validity of credentials. If the access token is expired, this will automatically use the refresh token to obtain a new access token.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0, access_type='offline')
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
    #endregion
    
    #region Building message and sending email
    def create_message_with_attachment(sender, to, subject, body, attachment):
        # Add sender, recipient, subject, and attach the body text
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        msg = MIMEText(body, 'html')
        message.attach(msg)

        # Guess the MIME type of the attachment, in this case it should be 'application/pdf'
        content_type, encoding = mimetypes.guess_type(attachment)
        # In case it fails to guess the MIME type, default to generic binary data
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        
        # Open file in binary mode, use its MIME type to create a MIME object, and set the content as the MIME object's payload
        with open(attachment, 'rb') as f:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(f.read())
        # Encode the payload in base64 to ensure it can be safely sent over email
        encoders.encode_base64(msg)

        # Extact filename from file path, add a header to indicate that this part is an email attachment, and then attach it to the main message
        filename = os.path.basename(attachment)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        # Convert entire email message to a bytes object, encode in base64, and then decode data into a raw string
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        return {'raw': raw}
    
    def send_message(service, user_id, message):
            message = service.users().messages().send(userId=user_id, body=message).execute()
    #endregion
    
    #region Fun
    def get_dad_joke():
        headers = {'Accept': 'application/json'}
        r = requests.get('https://icanhazdadjoke.com/', headers=headers)
        if r.status_code == 200:
            json_response = r.json()
            dad_joke = json_response['joke']
            return f"Dad joke of the day: <i>{dad_joke}</i>"
        else:
            return ""
    #endregion

    #region Iteration
    # Create the webdriver and the initial database, then iterate through each swimmer's URL
    driver = initialize_webdriver()
    connection, cursor = initialize_db()
    swimmer_id = 1
    for swimmer in SWIMMERS:
        # Get webpage
        driver.get(swimmer['url'])
        # Wait until table is loaded before proceeding. If it doesn't load, catch TimeoutException, quit webdriver, and exit main function
        try:
            # Waits for the best times table to be located
            WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, TABLE_XPATH))
                    )
        except TimeoutException:
            print("Failed to locate best times table.")
            print("Quiting...")
            driver.quit()
            return
        
        # General swimmer info
        scrape_swimmer_info_and_store_data()
        # Scrape SCY table
        scrape_table_and_store_data('SCY')
        # Switch to LCM table and scrape
        driver.find_element(By.XPATH, LCM_BUTTON_XPATH).click()
        scrape_table_and_store_data('LCM')
        # Increment swimmer_id before next iteration
        swimmer_id += 1
    #endregion

    #region Wrapping up
    # Quit webdriver
    driver.quit()
    # Commit and close connection to database
    connection.commit()
    connection.close()
    
    # Build CSV and convert to PDF now that data has been scraped, stored, and formatted
    build_csv()
    convert_csv_to_pdf()

    # Authenticate Gmail, compose email with attachment, and send
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    dad_joke_text = get_dad_joke()

    email_body = f"""<p>Please see the attached PDF.<br>The PDF contains the latest, best swim times for the provided swimmers.</p>
    <p>{dad_joke_text}</p><br>
    <p><b>This is an automated email message.</b></p>"""

    message = create_message_with_attachment(SENDER_EMAIL, RECIPIENT_EMAIL, EMAIL_SUBJECT, email_body, CSV_TO_PDF_OUTPUT)
    send_message(service, "me", message)
    #endregion

if __name__ == '__main__':
    main()