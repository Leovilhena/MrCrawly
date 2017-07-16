#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import datetime

# First attemp for a simple crawler to get info from a single page.
# It actually just craw into contact page for emails
# Can get links from pages, meta content and title.

# Functionalities to be added soon:
# - Analize texts, summerize paragraphs and compare to meta
# - Abbility to crawl deeper to get more info
# - Google up and get more from different websites of the same kind
# - Identify language and improve for Portuguese and Polish
# - Log procedures (make with errors)
# - Save info(title, meta, links, contact mail, maybe phone number) in a database
# - Should I make it with classes? This is just simple as it goes.
# - Fix many errors handling
#
# DONE IS BETTER THAN PERFECT!
#

def logger(url, title, meta, emails):
    """Simple logger, just to have a check what's been going on"""
    with open('crawly_diary.log', 'a+') as cd:
        cd.write('Date, "%s"\n' % str(datetime.datetime.now()))
        cd.write('Url, "%s"\n' % url)
        cd.write('Title, "%s"\n' % title.get_text())
        for content in meta:
            cd.write('Meta, "%s"\n' % content["content"])
        for email in emails:
            cd.write('Email, "%s"\n' % email)
        cd.write('***\n')


def printResults(title,meta,emails):
    """Just print our results """

    # Print for title
    if title == None or not title:
        print('\nNo title found :(\n')
    else:
        print('\nTitle:\n',title.get_text())

    # Print for meta
    if meta == None or not meta:
        print('\nNo meta found :(\n')
    else:
        print('\nMeta Tag:')
        for content in meta:
            print(content["content"])

    # Print for emails
    if emails == None or not emails:
        print('\nNo email found :(\n')
    else:
        print('\nContact emails:')
        for email in emails:
            print(email)


def getUrl():
    """Just get the input and move one"""
    try:
        url = input('Mr.Crawly: ')
        return url
    except as e:
        print('...so tragic...')
        print(e)
        pass

    return

def helper(u_input):
    """Our instructions and program options"""

    # Change user input to lower
    u_input = u_input.lower()

    # Check for program options
    if u_input == 'q':
        exit(0)
    elif u_input == 'h':
        print('\nJust type a website address to get contacts (english)')
        print('Press Q to quit')
        return True
    elif u_input == 'scream':
        print("\nPaste this in your browser to hear his call")
        print('https://www.youtube.com/watch?v=G3LvhdFEOqs')
        return True

    return False

def urlBuilder(url):
    """ Builds our url, if not well written"""

    # Splits url for checking, useful to add more features later
    split_url = urlsplit(url)

    # Variable declaration
    new_url = ""

    # if not given which protocol, put http as standard
    if not split_url.scheme:
        new_url = 'http://' + url
        return new_url
    else:
        return url

def makeRequest(url):
    """Requests given url """

    # Headers for request mobile version
    headers = {"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
                "Accept-Language":"en-US,en;q=0.5"}
    try:
        print('Mr.Crawling ...')
        # Our main request
        html  = requests.get(url, headers=headers)
        if html.status_code == requests.codes.ok:
            print('Page fetched!')
            return html.text

    except requests.exceptions.RequestException:
            # If didn't work, try to change protocol scheme
            if url[:5] == 'https':
                url = 'http' + url[5:]
            elif url[:5] == 'http:':
                url = 'https' + url[4:]
            else:
                print('Did you talk to the dead? Page not found!')
                return
            try:
                # Try again!
                html  = requests.get(url, headers=headers)
                if html.status_code == requests.codes.ok:
                    print('Page fetched!')
                    return html.text
            except:
                print('Did you talk to the dead? Page not found!')
                return

def bsObjCreator(url_text):
    """Creates a BeautifulSoup Object for scraping"""

    try:
        bsObj = BeautifulSoup(url_text, "lxml")
        return bsObj
    except AttributeError as e:
        print('Error: Lacks ingredients')

    return

def getLinks(bsObj):
    """Get all links from page and look for contact page and emails for contact"""

    # Sanity check
    if not bsObj or bsObj == None:
        return

    # List for links from our page
    page_links = set()
    # Set for unique contact links
    contact_links = set()
    # Set of emails
    emails = set()

    # Iterates through "href" tags
    for link in bsObj.findAll('a'):
        if 'href' in link.attrs:
            link = link.get('href')
        else:
            continue
            # Appends all links from website
        if 'http' in link:
            page_links.add(link)
            # Appends mails if is in tag
        elif 'mailto' in link:
            emails.add(link[7:])
            continue
        else:
            continue
        # If one of them is a contact, add to a set
        if re.search(r"[./a-z0-9-]+(contact)[./a-z0-9-]+", link, re.I) or re.search(r"[./a-z0-9-]+(about)[./a-z0-9-]+", link, re.I):
            # Adds link to our set
            print('Got some contact page!')
            contact_links.add(link)
        # Makes another request for this suposed contact page
            try:
                contact_page = requests.get(link)
                # Find all e-mails and creates a set with unique values
                all_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", contact_page.text, re.I))
                # If we have one
            except:
                pass

            # If we have a set of emails
            if all_emails:
                # Add to our first set
                for email in all_emails:
                    emails.add(email)
    return emails



# Welcome prints
print("\n'Uncovering things that were sacred and manifest on this Earth'")
print('Type H for help or scream!')
print("Type Q to exit but there is no scape!")

# Infinite loop for running
while(True):

    # Initial print
    print('\nWhat went on in your head?')

    # Getting your url
    first_input = getUrl()

    # Checking input for other options
    if helper(first_input):
        continue

    # Building url
    my_url = urlBuilder(first_input)

    # Making our request
    my_request = makeRequest(my_url)

    # If succeed create an BeautifulSoup Object
    if my_request:
        my_soup = bsObjCreator(my_request)
        # If we have na Bs Object, go ahead
        if my_soup:
            title = my_soup.head.title
            meta = my_soup.head.findAll("meta",{"name": {"description", "descriptions", "keywords", "keyword", "Description", "Descriptions", "Keywords", "Keyword"}})
            emails = getLinks(my_soup)
            printResults(title,meta,emails)
            logger(my_url,title,meta,emails)
