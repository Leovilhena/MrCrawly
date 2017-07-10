#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlsplit

# First attemp for a simple crawler to get info from a single page.
# It actually just craw into contact page for emails
# Can get links from pages, meta content and title.
# I did it in one day, so there's a lot of things to fix and improve
# Some functions got inspired by scraping sites and O'Relly books
# Need to clean up the code and comment BETTER
# Functionalities to be added soon:
# - Abbility to crawl deeper to get more info
# - Google up and get more from different websites of the same kind
# - Identify language and improve for Portuguese and Polish
# - Http and www encoders, you just write what you want and we'll do it for you
# - Add headers
# - Log procedures
# - Save info(title, meta, links, contact mail, maybe phone number) in a database
# - Should I make it with classes? This is just simple as it goes.
# - Separate all code into more functions, specially in the running Loops
# - Fix many errors handling
#
# DONE IS BETTER THAN PERFECT!
#

def resolveAnchorLink(url):
    # extract base url to resolve relative links
    parts = urlsplit(url)
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    path = url[:url.rfind('/')+1] if '/' in parts.path else url
    return path


def makeRequest(url):
    """ Request given url """
    try:
        print('Mr.Crawling ...')
        html  = requests.get(url)
        if html.status_code == requests.codes.ok:
            print('Page fetched!')
            return html.text
    except requests.exceptions.RequestException as e:
            print('Did you talk to the dead? Page not found!')
            return

def bsObjCreator(url_text):
    """ Creates a BeautifulSoup Object for scraping"""

    try:
        bsObj = BeautifulSoup(url_text, "lxml")
        return bsObj
    except AttributeError as e:
        print('Error: Lacks ingredients')

    return

        # Add more arguments and make it one function
def getTitle(bsObj):
    """Function that gets title from html pages"""
    try:
        return bsObj.head.title
    except:
        pass

        return None

def getMetaTag(bsObj):
    try:
        return bsObj.head.findAll("meta",{"name": {"description", "descriptions", "keywords", "keyword", "Description", "Descriptions", "Keywords", "Keyword"}})
    except:
        pass

    return None

# Create other functions related to this or separate this one?
def getLinks(bsObj):

    if not bsObj or bsObj == None:
        return None

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
            emails.add(link)
            continue
        # NEED TO HANDLE links without full url
        elif link.startswith('/'):
            resolveAnchorLink(url)
            link = base_url + link
        else:
            continue
        # If one of them is a contact, add to a set
        if re.search(r"[./a-z0-9-]+(contact)[./a-z0-9-]+", link, re.I) or re.search(r"[./a-z0-9-]+(about)[./a-z0-9-]+", link, re.I):
        # Adds link to our set
            contact_links.add(link)
        # Makes another request for this suposed contact page
            try:
                contact_page = requests.get(link)
                # Find all e-mails and creates a set with unique values
                all_emails = set(re.findall(r"[a-z0-9\._+]+@[a-z0-9\.\-+_]+\.[a-z]*", contact_page.text, re.I))
                # If we have one
                if all_emails:
                    # Add to our first set
                    for email in all_emails:
                        emails.add(email)
            except:
                pass

    if emails:
        return emails
    else:
        return





# Variables
title = None
meta = None



# CREATE a UI for input and choose action?
# Infinite loop for running
while(True):
    print("Type Q to exit!\n")

    # Url Input
    my_url = input("Mr.Crawly: ")

    # Quit condition
    if my_url.lower() == 'q':
        break

    #Finish url if needed *FIX LENGTH*
    if len(my_url) < 4:
        continue

    if 'www.' in my_url[:4].lower() or '.io' in my_url:
    # Try to concatenate http://
        try:
            full_url = "http://" + my_url
            my_request = makeRequest(full_url)

            if my_request:
                my_soup = bsObjCreator(my_request)
                if my_soup:
                    title = getTitle(my_soup)
                    meta = getMetaTag(my_soup)
                    emails = getLinks(my_soup)
            else:
                pass
        except:
            # Try again to concatenate https://
            try:
                full_url = "https://" + my_url
                my_request = makeRequest(full_url)

                if my_request:
                    my_soup = bsObjCreator(my_request)
                    if my_soup:
                        title = getTitle(my_soup)
                        meta = getMetaTag(my_soup)
                        emails = getLinks(my_soup)
            except:
                pass
    elif 'http://' in my_url[:7].lower() or 'https://' in my_url[:8].lower():
        my_request = makeRequest(my_url)

        if my_request:
            my_soup = bsObjCreator(my_request)
            if my_soup:
                title = getTitle(my_soup)
                meta = getMetaTag(my_soup)
                emails = getLinks(my_soup)


    # Printing procedures and validation check
    if title == None or not title:
        print('\nNo title found :(\n')
    else:
        print('\nTitle:\n',title.get_text())

    if meta == None or not meta:
        print('\nNo meta found :(\n')
    else:
        print('\nMeta Tag:')
        for content in meta:
            print(content["content"])

    if emails == None or not emails:
        print('\nNo email found :(\n')
    else:
        print('\nContact emails:')
        for contact in emails:
            print(contact,'\n')
