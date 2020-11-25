from bs4 import BeautifulSoup
from datetime import date
import requests
import smtplib
import urllib
import pickle
import re
import os

# May add revolving headers later....
UNIXHEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"}

# May need to change path if you change location of buffer and email file
BUFFER_FILE = "/home/pi/Desktop/pi-price-scraper/currentPrices.buf"
EMAIL_FILE = "/home/pi/Desktop/emailCreds.txt"

############################ Email Functions ############################

# Utility for getEmailCreds()
def extractEmailInfoLine(line, tag, filterReg):
    # Grab tag location
    searchResults = re.search(tag, line)
    if (searchResults != None):
        # Use tag location to grab rest of line
        lineAfterFound = line[searchResults.end():]
        # Get content after tag (password or email)
        searchResults = re.search(filterReg, lineAfterFound)
        if (searchResults != None):
            return searchResults.group()
    # Return empty string if extraction is unsuccessful
    return ""
    ################# End Function #################

# Get sender email, password, and receiver email  from EMAIL_FILE
def getEmailCreds():
    # Initialize to detect errors
    to_email = from_email = password = ""

    # Open EMAIL_FILE and get the full file (since it should only be 3 lines)
    with open(EMAIL_FILE, 'r') as reader:
        bufList = reader.readlines()

    from_email = extractEmailInfoLine(bufList[0], r"FROM_EMAIL:", r"\S+@\S+\.\S+")
    password = extractEmailInfoLine(bufList[1], r"PASS.*:", r"\S+")
    to_email = extractEmailInfoLine(bufList[2], r"TO_EMAIL:", r"\S+@\S+\.\S+")

    # Kill program if even just one fails to be obtained
    if ((from_email == "") or (to_email == "") or (password == "")):
        raise Exception("Email and password were not successfully retrieved!")

    # Return each as lower except for case sensitive password
    return from_email.lower(), password, to_email.lower()
    ################# End Function #################

def sendEmail(sender, sender_password, receiver, mailBody):
    # Get and format date for subject header
    formattedDate = date.today().strftime("%B %d, %Y")
    # Signal HTML syntax and set the Subject
    mailtext = "Content-type: text/html\nSubject: A Price Dropped On Your Watchlist! (" \
               + formattedDate + ")\n\n"
    mailtext += mailBody

    # Set up email signals
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.ehlo()
    server.starttls()
    # Log into mail and send the email
    server.login(sender, sender_password)
    server.sendmail(sender, receiver, mailtext)
    ################# End Function #################

############################ Utility Function ###########################

# Find class set for instances like promotion sets
def bsClassFindPrice(page, classID):
    parsedPage = BeautifulSoup(page, 'html.parser')
    findResults = parsedPage.find("div", class_=classID)
    if (findResults == None):
        raise Exception("Class not found: {classID}")
    return findResults.get_text()
    ################# End Function #################

# Use as utility for converting default error dump to product-retailer specific file name
def changeFileName(oldFileName, newFileName):
    os.rename(oldFileName, newFileName)
    ################# End Function #################

# Dump page to "errorDump.html" so that the product and retailer can be appended in caller functions
def dumpPageToLog(page):
    with open("errorDump.html", 'w') as file:
        file.write(page)
    ################# End Function #################

# Download the raw HTML file via one of two methods and return it as a string
def getHTMLText(url, requestLibPath=False, headParams=UNIXHEADERS):
    # Download via Requests library
    if (requestLibPath):
        with requests.get(url, headers=UNIXHEADERS) as page:
            html = page.content
    # Else download via urllib
    else:
        # Assemble request header for urllib
        req = urllib.request.Request(url, data=None, headers=headParams)
        # Retrieve HTML page and dump as a string into variable
        with urllib.request.urlopen(req) as filepage:
            html = filepage.read().decode('utf-8')
    
    if (html == None):
        raise Exception("Webpage was unsuccessful in downloading")
    return str(html)
    ################# End Function #################

def getStringRegexResult(page, priceRegex, hardException=True):
    # Search the string for the regex pattern
    regResult = re.search(priceRegex, page)
    if (regResult != None):
        return regResult.group()
    # Allow for choosing between hard & soft errors to be able to parse file multiple times
    if (hardException):
        # Dump the string to see what was actually being searched
        dumpPageToLog(page)
        raise Exception(f"Result not found via supplied regex: {priceRegex}")
    return "" 
    ################# End Function #################

# Obtain HTML formatted retailer entry string for email
def getHTMLRetailerEntry(retailer, link, prevPrice, newPrice):
    # Hyperlink the product link to the retailer tax
    linkHtml = '<a href="' + link + '">' + retailer.capitalize() + ':</a> '
    priceMsg = 'Price drop from $' + prevPrice + " to $" + newPrice + "</p>\n"
    # Combine link and price with tab spacing for full HTML entry
    htmlStr = "<p>&nbsp;&nbsp;&nbsp;" + linkHtml + priceMsg
    return htmlStr
    ################# End Function #################

# Format promotion list in HTML syntax
def getHTMLRetailerPromo(promoList, retailer="", link=""):
    htmlStr = "<p>"
    # Add retailer header if requested
    if (retailer != ""):
        htmlStr += '&nbsp;&nbsp;&nbsp;<a href="' + link + '">' + \
                    retailer.capitalize() + ':</a></p>\n<p>'
    
    # Add promo header
    htmlStr += "&nbsp;&nbsp;&nbsp;Promos:</p>\n"
    # Represent two non breakable HTML 3 space tabs
    twoTabs = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    for promo in promoList:
        htmlStr += "<p>" + twoTabs + promo + "</p>\n"
    return htmlStr
    ################# End Function #################

######################## Serialization Functions ########################

# Write object list to binary formatted file
def serializeList(objList):
    # File opened is relative to working directory
    with open(BUFFER_FILE, 'wb') as file:
        pickle.dump(objList, file)
    ################# End Function #################

# Retrieve object list from binary formatted file
def deserializeList():
    # File opened is relative to working directory
    with open(BUFFER_FILE, 'rb') as file:
        objList = pickle.load(file)
    return objList
    ################# End Function #################

############################### Retailers ###############################

def findAmazonPrice(url):
    page = getHTMLText(url)
    # Try to look for alternative price format
    searchResult = getStringRegexResult(page, r"data-asin-price=\"\d*\.\d*", hardException=False)
    if (searchResult != ""):
        return float(searchResult[17:]), []
    # Try to look for normal price format
    searchResult = getStringRegexResult(page, r"priceblock_ourprice\".*<", hardException=False)
    if (searchResult != ""):
        price = getStringRegexResult(searchResult, r"\d+\.\d+")
        return float(price), []
    # Try to look for daily deal price and throw hard exception if unsuccessful
    searchResult = getStringRegexResult(page, r"priceblock_dealprice.*\n.*")
    price = getStringRegexResult(searchResult, r"\d+\.\d+")
    return float(price), []
    ################# End Function #################

def findWalmartPrice(url):
    page = getHTMLText(url)
    priceContainer = bsClassFindPrice(page, "prod-PriceHero")
    price = getStringRegexResult(priceContainer, r"\d+\.\d+")
    return float(price), []
    ################# End Function #################

############################# Tech Retailers ############################

def findBestBuyPrice(url):   # Detects price even if sold out
    page = getHTMLText(url, requestLibPath=True)
    priceContainer = bsClassFindPrice(page, "priceView-hero-price priceView-customer-price")
    price = getStringRegexResult(priceContainer, r"\d*\.\d*")
    return float(price), []
    ################# End Function #################

def findBHPhotoPrice(url):
    page = getHTMLText(url)
    price = getStringRegexResult(page, r"pricingPrice.*?\d*\.\d*")
    price = price[15:]
    # Extract coupon container with regex
    couponStr = getStringRegexResult(page, r"savingCouponContainer.*?</div", hardException=False)
    if (couponStr != ""):
        # Extract coupon description from container and kick out the framing characters
        regResult = getStringRegexResult(couponStr, r"g>.*</d")
        if (regResult != ""):
            return price, [regResult[2:-3]]
    return float(price), []
    ################# End Function #################

def findNeweggPrice(url):
    page = getHTMLText(url)
    price = getStringRegexResult(page, r"product_sale_price.*?\d*\.\d*")
    return float(price[21:]), []
    ################# End Function #################

############################ Music Retailers ############################

def findGuitarCenterPrice(url):
    page = getHTMLText(url)   # Get page
    # Get 2 line regex result for topAlignedPrice class (easier than BS extraction)
    searchResult = getStringRegexResult(page, r"topAlignedPrice.*\n.*")
    return float(getStringRegexResult(searchResult, r"\d*\.\d*")), []   # Extract price number from topAlignedPrice class
    ################# End Function #################

def findMusiciansFriendPrice(url):
    page = getHTMLText(url)
    parsedPage = BeautifulSoup(page, 'html.parser')
    skuDetails = parsedPage.find(id="skuDetail")
    if (skuDetails != None):
        searchResult = getStringRegexResult(skuDetails.get_text(), r"salePrice=\d*.\d*")
        return float(searchResult[10:]), []
    
    productDetails = getStringRegexResult(page, r"siteVars hidden.*\n.*")
    priceStr = getStringRegexResult(productDetails, r"\d+\.\d+")
    return float(priceStr), []
    ################# End Function #################

def findSweetwaterPrice(url):
    page = getHTMLText(url)
    parsedPage = BeautifulSoup(page, 'html.parser')
    # Extract the price
    priceProp = parsedPage.find(property="product:price:amount")
    if (priceProp == None):
        dumpPageToLog(page)
        raise Exception("Price property not found for Sweetwater")
    price = getStringRegexResult(str(priceProp), r"\d+\.\d+")
    
    # Search for promos
    promoStrList = []
    promoClass = parsedPage.find_all("div", class_="product-promo__body")
    if (len(promoClass) != 0):
        for newPromoStr in promoClass:
            promoStrList.append(newPromoStr.contents[0].strip())
    return float(price), promoStrList
    ################# End Function #################

# Jump table for retailer to retailer processing function mapping
URL_PROCESSOR_MAPPER = {"amazon":           findAmazonPrice,
                        "bestbuy":          findBestBuyPrice,
                        "bhphoto":          findBHPhotoPrice,
                        "guitarcenter":     findGuitarCenterPrice,
                        "musiciansfriend":  findMusiciansFriendPrice,
                        "newegg":           findNeweggPrice,
                        "sweetwater":       findSweetwaterPrice,
                        "walmart":          findWalmartPrice}