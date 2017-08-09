#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urljoin
import datetime
import json
import os
import np_x
from np_x import NPExtractor

# First attemp for a simple crawler to get info from a single page.
# It actually just craw into contact page for emails
# Can get links from pages, meta content and title.

# Recently update! Just add NLP for what's page is about. It's in beta test

# Functionalities to be added soon:
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

def openFile(path):
    with open(path,'r') as address_list:
        link_list = list(set(email.replace("\n", "") for email in address_list if email))
    return link_list

def logger(results, loaded={}):
    # Now time as key for dictionary
    date = str(datetime.datetime.now())

    # Check for file in disk
    if os.path.isfile('crawly_diary.json'):
        # Open file and load, if not a JSON create a dict for it
        with open('crawly_diary.json', 'r') as log:
            loaded = json.load(log)

    # Open file and save as a JSON
    with open('crawly_diary.json', 'w+') as log:
        loaded[date] = results
        json.dump(loaded, log, indent=2)


def printResults(title,about,meta,emails):
    """Just print our results """

    # Print for title
    if not title:
        print('\nNo title found :(\n')
    else:
        print('\nTitle:\n',title)

    if not about:
        print('\nNothing found about it :(\n')
    else:
        print('\nAbout:\n',", ".join(about))

    # Print for meta
    if not meta:
        print('\nNo meta found :(\n')
    else:
        print('\nMeta Tag:')
        for content in meta:
            print(content["content"])

    # Print for emails
    if not emails:
        print('\nNo email found :(\n')
    else:
        print('\nContact emails:')
        for email in emails:
            print(email)


def getUrl():
    """Just get the input and move on"""
    try:
        url = input('Mr.Crawly: ')
        return url
    except:
        print('...so tragic...')
        exit(1)


def helper(u_input):
    """Our instructions and program options"""

    # Change user input to lower
    u_input = u_input.lower()

    # Check for program options
    if u_input == 'q':
        exit(0)
    elif u_input == 'o':
        path = input('Type file name: ')
        link_list = openFile(path)
        for link in link_list:
            print('\n' + link)
            Crawling(link)
        return True

    elif u_input == 'h':
        print('\nJust type a website address to get contacts (english)')
        print('Type O to open a file')
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

    # if not given which protocol, put http as standard
    if not split_url.scheme:
        return 'http://' + url
    else:
        return url

def makeRequest(url):
    """Requests given url """
    # Sanity check
    if not url:
        return

    # Headers for request mobile version
    headers = {"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
                "Accept-Language":"en-US,en;q=0.5"}
    try:
        print('\nMr.Crawling ...')
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

    return None

def getLinks(bsObj, baseurl):
    """Get all links from page and look for contact page and emails for contact"""

    # Sanity check
    if not bsObj:
        return

    # Returning dictionary of sets
    info = {'xpages': set(), 'contact_pages': set(), 'emails':set()}

    # Iterates through "href" tags
    for link in bsObj.findAll('a'):
        # If we have 'href' tag go ahead
        if 'href' in link.attrs:
            # NEED TO FIX FOR LINK NOT WELL WRITTEN
            link = link.get('href')
        # Else, skip and loop again
        else:
            continue

        # If it's a mailto send it to emails set, check if there's a email address inside
        if 'mailto' in link and bool(re.search(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", link, re.I)):
            info['emails'].add(link[7:])
            continue

        # Adds to our set http links from website
        if 'http' in link:
            info['xpages'].add(link)
            # If it's a contact type add to contact_pages
            if contactFinder(link):
                info['contact_pages'].add(link)

        # Adds paths to our links
        elif '/' in link:
            # Assuming that we have just one baseurl passed join with the path found
            fixed_link = urljoin(baseurl,link)
            info['xpages'].add(fixed_link)
            # If it's a contact type add to contact_pages
            if contactFinder(fixed_link):
                info['contact_pages'].add(fixed_link)

    return info


def contactFinder(text):
    """Check with REGEX for contact types"""
    if re.search(r"[./a-z0-9-]+(contact)[./a-z0-9-]+", text, re.I) or re.search(r"[./a-z0-9-]+(about)[./a-z0-9-]+", text, re.I):
        return True
    else:
        return False

def getMails(info):
    """Function to get crawl and scrap contact emails"""

    try:
        for page in info['contact_pages']:
            # Make a request
            contact_page = requests.get(page)
            # Find all e-mails with REGEX and update to our set
            info['emails'].update(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", contact_page.text, re.I))
    except requests.exceptions.RequestException as e:
        print('Connection problems:')
        print(e)

    # Return as a list for serializing in JSON
    return list(info['emails'])

def Crawling(url):
    # Building url
    my_url = urlBuilder(url)

    # Making our request
    my_request = makeRequest(my_url)

    # If succeed create an BeautifulSoup Object
    if my_request:
        my_soup = bsObjCreator(my_request)

        # If we have na Bs Object, go ahead
        if my_soup:
            # Get title tag
            title = my_soup.head.title.text

            # NLP for topics
            np_extractor = NPExtractor(title)
            about = np_extractor.extract()

            # Get all meta tagas for name and description of website
            metas = my_soup.head.findAll("meta",{"name": {"description", "descriptions", "keywords", "keyword", "Description", "Descriptions", "Keywords", "Keyword"}})

            # Get all emails from contact pages
            emails = getMails(getLinks(my_soup,my_url))

            # Print out
            printResults(title,about,metas,emails)

            # Compiling all results!
            final_results ={'url':my_url,'title':title, 'topics':about, 'emails': emails,'meta':[meta['content'] for meta in metas]}

            # Saving/logging activities
            logger(final_results)


# Welcome prints
print("\n'Uncovering things that were sacred and manifest on this Earth'")
print('Type H for help or scream!')
print('Type Q to exit but there is no scape!')
print('Type O to unlock the gates of a file!')

# Infinite loop for running
def main():
    while(True):
        # Initial print
        print('\nWhat went on in your head?')

        # Getting your url
        first_input = getUrl()

        # Checking input for other options
        if helper(first_input):
            pass
        else:
            Crawling(first_input)


if __name__ == '__main__':
    main()
