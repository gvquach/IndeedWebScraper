# Set your preferences for your job search

# how many pages do you want to scrape per search query
NUM_PAGES_PER_SEARCH = 5

# words for your search query, only 1-4 word phrases
SEARCH_LIST = [
    #'Fall Intern',
    #'Software Engineer intern fall',
    #'Software Developer intern fall',
    #'Software fall 2020',
    'Software Engineer Intern',
]

# which companies do you want to filter out
FILTERED_COMPANIES = [
    'Oigetit',
    'GoGoody',
]

# which titles do you want to filter out
FILTERED_TITLES = [
    'Unpaid',
    'Graduate',
]

# any word that must be in your title  
PRIORITY_TITLES = [
    'Software',
    'Developer',
    'Backend',
    'Fullstack',
    'Full-stack',
    'Back-end',
]

# the email address + password of the GMAIL account that will send our your emails
MY_ADDRESS = 'whataddress@gmail.com'
PASSWORD = 'whatismypw'

# location of your JobScrape_DB.db file
DB_FILE_LOCATION = r"FILE_LOCATION\JobScraper_DB.db"

# 'name email' of the email you want the message sent to
RECIPIENT_EMAILS = [
    'name email',
    'name email',    
]