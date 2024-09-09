# Purpose
This is a project that I was assigned during a job interview in early 2024. I succeeded in finishing the project, and it received approval from the hiring manager. In summary, its goal is to automatically scrape swimmers' best time results from [SwimStandards](https://swimstandards.com/) using provided URLs, store the scraped data in a database, generate a PDF using said data, and emailing the PDF to a provided recipient address every morning.

# Assignment Requirements
1. Fetch swimming best times for individual swimmer(s), nightly
2. Store in database such that it can be queried later
3. Generate PDF report summarizing prior day’s information
4. Email PDF report (attached, not linked) by the following morning
5. Utilize one backend API call to accomplish the task, e.g. Google API for email

# Usage
1. Follow the steps from Google's [Python quickstart page](https://developers.google.com/gmail/api/quickstart/python) for authentication and authorization
   * Include `https://www.googleapis.com/auth/gmail.send` as one of the scopes in the quickstart.py file
2. Modify the **SWIMMERS** list variable in [constants.py](/constants.py)
   * Each element in the list is a dictionary able to contain the birthdate and SwimStandards URL for an individual swimmer
   * The birthdate format does not matter
   * Example URL: `https://swimstandards.com/swimmer/rylee-erisman`
   * As expected, more than one swimmer can be added to the list
3. Modify the **SENDER_EMAIL** and **RECIPIENT_EMAIL** variables in [constants.py](/constants.py)
4. Run [main.py](/main.py)
5. Automate using a cron job, Windows Task Scheduler, etc. to run [main.py](/main.py) daily

# Modules/APIs Used and Their Purposes
1. base64
   * Encode the email message before decoding into raw string
2. csv
   * Build the CSV file
3. mimetypes
   * Determine the content type and encoding of attachment
4. os
   * Simplify filename and filepath handling
5. email
   * Build the email message with attached PDF
6. requests
   * Send an HTTP GET request to the icanhazdadjoke API
7. sqlite3
   * Build database
8. csv2pdf
   * Convert the CSV to a PDF file
9. Selenium
   * Load the webpage(s) and scrape text data
10. Google's Gmail API
    * Send final email through Gmail
11. [icanhazdadjoke API](https://icanhazdadjoke.com/) (Daily dad joke for fun)
    * Include random dad joke in daily email - because, why not?