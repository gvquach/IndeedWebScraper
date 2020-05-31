# Indeed Job Scraper

A Python script that scrapes Indeed.com job listings

## Features

* Allow multiple different keyword search queries
    * Specify how many pages to scrape per search query
    * Specify certain companies and positions to filter out
    * Specify certain positions to prioritize
* Stores newly found job listings into an SQLite database
    * Increments the date posted of every posting in our database every time the script is ran (Maybe setup your own AWS EC2 instance to schedule the script to run once a day?)
    * Deletes any job listings in our database that has a date posted of more than 29 days ago
* Sends out email notifications for newly posted roles via a local SMTP server
    * If no new postings are found, sends a template email instead (Sanity check)

## Files

**web-scraper.py:** Main file to scrape the web and to choose which postings will be inserted into our SQLite database

**sendEmail.py:** Sends out the email via a local SMTP server

**settings.py:** Setup your file locations and search preferences

**emailBody.txt:** Text file used to compile the body of the email


## Configuration (Hosting on a local computer)

### `pip install selenium`
### `pip install bs4`
### `pip install webdriver_manager`

* Setup all your settings/preferences found in settings.py
* Create an empty text file in our working directory called: emailBody.txt
* Once you are done with that, run our script using:
### `$ python web-scraper.py`

## Troubleshooting

* If you get a 'This version of ChromeDriver only supports Chrome Version XXX' error, you can find a solution at this link:
 https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome


## Notes

* Host the python application on AWS and use crontab to schedule it to run once a a day for best results
