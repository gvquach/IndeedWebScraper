from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import re
import sqlite3
import sendEmail
import os
from selenium.webdriver.chrome.options import Options
from settings import NUM_PAGES_PER_SEARCH, SEARCH_LIST, FILTERED_COMPANIES, FILTERED_TITLES, PRIORITY_TITLES

'''
PC - > AWS
------------
ChromeDriver setup
sendEmail - attachment file location
'''
# setup our driver and dataframe
def main():
    '''
    # AWS chromedriver setup
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1400,1500")
    driver = webdriver.Chrome(options=options)
    '''
    # Personal computer chromedriver setup
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # Connect to SQLite db and initialize cursor
    conn = sqlite3.connect('JobScraper_DB.db')
    c = conn.cursor()
    # create our JOBS table
    c.execute('CREATE TABLE IF NOT EXISTS JOBS(Company, Title, Date_Posted, Location, Link, Crunchbase, Glassdoor)')
    # make a list of our 'links' that are already in our table
    c.execute('SELECT DISTINCT Link FROM JOBS;')
    dbLinks = c.fetchall()
    parsed_links = [link for item in dbLinks for link in item]
    # make our dataframe
    dataframe = pd.DataFrame(columns=["Company", "Title", "Date_Posted", "Location", "Link", "Crunchbase", "Glassdoor"])
    # filter our dataframe to the job postings that we want
    dataframe = choosePostings(driver, dataframe, c, parsed_links)
    # fill our SQLite db
    createDB(dataframe, c, conn)
    # if our emailBody.txt file has stuff in it, email it
    if os.stat('emailBody.txt').st_size != 0:
        sendEmail.main()
        print('New jobs sent to email')
    # otherwise email our blank email template
    else:
        blankEmail()
        sendEmail.main()
        print('No new jobs found')
    # empty our emailBody.txt file for the next time we run our python script
    open('emailBody.txt', 'w').close()
    print('100% Completed')

# Append our dataframe to our SQLite db
def createDB(dataframe, c, conn):
    dataframe = dataframe.drop_duplicates()
    incrementDates(c, conn)
    conn.commit()
    dataframe.to_sql('JOBS', conn, if_exists = 'append', index = False)

# increment all dates in our SQLite db and delete any rows that have a date_posted > 29
def incrementDates(c, conn):
    # go through our date_posted updating row values in a backwards fashion so our dates don't all end up being set to 29
    for i in range(30, 1, -1):
        if i == 2:
            multiple_days = """
                UPDATE JOBS
                SET Date_Posted = '{0} days ago' 
                WHERE Date_Posted = '{1} day ago'
            """.format(i, i-1)
        else:
            multiple_days = """
                UPDATE JOBS
                SET Date_Posted = '{0} days ago' 
                WHERE Date_Posted = '{1} days ago'
            """.format(i, i-1)
        c.execute(multiple_days)
    one_day_query = """
        UPDATE JOBS
        SET Date_Posted = '1 day ago' 
        WHERE Date_Posted = 'Just posted' OR Date_Posted = 'Today'
    """
    c.execute(one_day_query)
    # delete values of 30 days ago
    delete_query = """
        DELETE FROM JOBS
        WHERE Date_Posted = '30 days ago'
    """
    c.execute(delete_query)

# parse the search into our hyperlinks
def keywordSearch(phrase):
    phrase = phrase.split(' ')
    size = len(phrase)
    if size == 1:
        hyperlink = "https://www.indeed.com/jobs?q={0}&l=California&sort=date".format(phrase[0])
    if size == 2:
        hyperlink = "https://www.indeed.com/jobs?q={0}+{1}&l=California&sort=date".format(phrase[0], phrase[1])
    if size == 3:
        hyperlink = "https://www.indeed.com/jobs?q={0}+{1}+{2}&l=California&sort=date".format(phrase[0], phrase[1], phrase[2])
    if size == 4:
        hyperlink = "https://www.indeed.com/jobs?q={0}+{1}+{2}+{3}&l=California&sort=date=".format(phrase[0], phrase[1], phrase[2], phrase[3])
    return hyperlink


# fill our dataframe with chosen job posting information
def choosePostings(driver, dataframe, c, parsed_links):
    # loop thru multiple pages
    for phrase in SEARCH_LIST:
        for page in range(0, NUM_PAGES_PER_SEARCH*10, 10):
            hyperlink = keywordSearch(phrase)
            if page == 0:
                driver.get(hyperlink)
            else:
                driver.get(hyperlink + str(page))
            postings = driver.find_elements_by_class_name('result')
            # loop thru all of the job postings on the page, and select the CSS data that we want
            for job in postings:
                result = job.get_attribute('innerHTML')
                soup = BeautifulSoup(result, 'html.parser')
                date_posted = soup.find(class_="date").text
                if date_posted == '30+ days ago':
                    continue
                company = soup.find(class_="company").text.replace('\n', '').strip()
                # filter out any companies that we don't want
                if any(c_word in company for c_word in FILTERED_COMPANIES):
                    continue
                title = soup.find('a', class_='jobtitle').text.replace('\n', '')
                # filter out any titles that we don't want
                if any(t_word in title for t_word in FILTERED_TITLES):
                    continue
                # must have one of the words in PRIORITY_TITLES in the job posting title
                if any(pt_word in title for pt_word in PRIORITY_TITLES):
                    pass
                else:
                    continue
                location = soup.find(class_="location").text
                parsed_location = location.split(',', 1)[0]
                list_links = soup.find('a', href = True)
                link = 'indeed.com' + list_links['href']
                # if the link already exists in our database - continue
                if parsed_links and link in parsed_links:
                    continue
                crunchbase = 'crunchbase.com/' + company
                glassdoor = 'glassdoor.com/' + company
                # email our message
                emailMsg(company, title, date_posted, location, link)
                # append the job posting to our dataframe        
                dataframe = dataframe.append({'Company': company, 'Title': title, 'Date_Posted': date_posted, 'Location': parsed_location, "Link": link, "Crunchbase": crunchbase, "Glassdoor": glassdoor}, ignore_index=True)
    return dataframe

# create the message (text file) for our email to be sent
def emailMsg(company, title, date_posted, location, link):
    with open('emailBody.txt', 'r') as f:
        content = f.read()
    with open('emailBody.txt', 'a') as f:
        if link in content:
            pass
        else:
            # can change this to just posted and today
            if date_posted == 'Just Posted' or date_posted == '1 day ago':
                f.write('{0}, {1}, {2}, {3}, {4}\n'.format(company, title, date_posted, location, link))

# no new jobs email template
def blankEmail():
    with open('emailBody.txt', 'w') as f:
        f.write('No new jobs found today.')

if __name__ == '__main__':
	main()