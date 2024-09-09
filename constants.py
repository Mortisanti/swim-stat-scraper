# Birthdates and URLs for scraping
SWIMMERS = [
    {'birthdate': '', 'url': ''}
    ]

# Generated filenames
CSV_OUTPUT = 'Swim Results.csv'
CSV_TO_PDF_OUTPUT = 'Swim Results (From CSV).pdf'
XLSX_OUTPUT = 'Swim Results.xlsx'
HTML_OUTPUT = 'Swim Results.html'
HTML_TO_PDF_OUTPUT = 'Swim Results (From HTML).pdf'

# XPATH strings for Selenium
TABLE_XPATH = '/html/body/div/div/div[2]/div[3]/div[2]/div/div[2]/table'
LCM_BUTTON_XPATH = '/html/body/div/div/div[2]/div[3]/div[2]/div/div[1]/a[2]'
NAME_XPATH = '/html/body/div/div/div[2]/div[1]/div/h1'
AGE_XPATH = '/html/body/div/div/div[2]/div[1]/div/div/div/div[1]'

# DB table names
TABLE_NAME_SWIMMERS = 'swimmers'
TABLE_NAME_BEST_TIMES = 'best_times'

# DB queries
SQL_CREATE_SWIMMERS_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME_SWIMMERS} (
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    current_age INTEGER,
    birthdate TEXT
);
"""

SQL_CREATE_BEST_TIMES_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME_BEST_TIMES} (
    id INTEGER PRIMARY KEY,
    swimmer_id INTEGER,
    event TEXT,
    best_time TEXT,
    standard TEXT,
    points TEXT,
    age INTEGER,
    meet TEXT,
    meet_date TEXT,
    FOREIGN KEY (swimmer_id) REFERENCES {TABLE_NAME_SWIMMERS} (id)
);
"""

# Google/Gmail API
# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SENDER_EMAIL = ''
RECIPIENT_EMAIL = ''
EMAIL_SUBJECT = "Latest Swim Results"