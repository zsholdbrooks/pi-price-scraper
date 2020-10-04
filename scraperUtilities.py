import requests
import urllib
from bs4 import BeautifulSoup
import smtplib
import re
import pickle
import os

UNIXHEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"}
BUFFER_FILE = "/home/pi/Desktop/pi-price-scraper/currentPrices.buf"

EMAIL_FILE = "/home/pi/Desktop/emailCreds.txt"

############################ Email Functions ############################

def changeFileName(oldFileName, newFileName):
    os.rename(oldFileName, newFileName)

def extractEmailInfoLine(line, tag, filterReg):
    searchResults = re.search(tag, line)
    if (searchResults != None):
        lineAfterFound = line[searchResults.end():]
        searchResults = re.search(filterReg, lineAfterFound)
        if (searchResults != None):
            return searchResults.group()
    # Return empty string if extraction is unsuccessful
    return ""

def getEmailCreds():
    to_email = from_email = password = ""

    with open(EMAIL_FILE, 'r') as reader:
        bufList = reader.readlines()

    from_email = extractEmailInfoLine(bufList[0], r"FROM_EMAIL:", r"\S+@\S+\.\S+")
    password = extractEmailInfoLine(bufList[1], r"PASS.*:", r"\S+")
    to_email = extractEmailInfoLine(bufList[2], r"TO_EMAIL:", r"\S+@\S+\.\S+")

    if ((from_email == "") or (to_email == "") or (password == "")):
        raise Exception("Email and password were not successfully retrieved!")

    return from_email.lower(), password, to_email.lower()

def sendEmail(sender, sender_password, receiver, mailBody):
    mailtext = "Content-type: text/html\nSubject: A Price Dropped On Your Watchlist!\n\n"
    mailtext += mailBody

    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.ehlo()
    server.starttls()
    server.login(sender, sender_password)
    server.sendmail(sender, receiver, mailtext)

############################ Utility Function ###########################

def getHTMLText(url, requestLibPath=False, headParams=UNIXHEADERS):
    req = urllib.request.Request(url, data=None, headers=headParams)
    
    if (requestLibPath):
        with requests.get(url, headers=UNIXHEADERS) as page:
            html = page.content
    else:
        req = urllib.request.Request(url, data=None, headers=headParams)
        with urllib.request.urlopen(req) as filepage:
            html = filepage.read().decode('utf-8')
    
    if (html == None):
        raise Exception("Webpage was unsuccessful in downloading")
    return str(html)

def getStringRegexResult(page, priceRegex, couponRegex="", hardException=True):
    regResult = re.search(priceRegex, page)
    if (regResult != None):
        return regResult.group()
    if (hardException):
        dumpPageToLog(page)
        raise Exception(f"Result not found via supplied regex: {priceRegex}")
    return "" 

def bsClassFindPrice(page, classID):
    parsedPage = BeautifulSoup(page, 'html.parser')
    findResults = parsedPage.find("div", class_=classID)
    if (findResults == None):
        raise Exception("Class not found: {classID}")
    return findResults.get_text()

def dumpPageToLog(page):
    with open("errorDump.html", 'w') as file:
        file.write(page)

def getHTMLRetailerEntry(retailer, link, prevPrice, newPrice):
    linkHtml = '<a href="' + link + '">' + retailer.capitalize() + ':</a> '
    priceMsg = 'Price drop from $' + prevPrice + " to $" + newPrice + "</p>\n"
    htmlStr = "<p>&nbsp;&nbsp;&nbsp;" + linkHtml + priceMsg
    return htmlStr

def getHTMLRetailerPromo(promoList, retailer="", link=""):
    htmlStr = "<p>"
    if (retailer != ""):
        htmlStr += '<a href="' + link + '">' + retailer.capitalize() \
                 + ':</a></p>\n<p>'
    else:
        htmlStr += "&nbsp;&nbsp;&nbsp;Promos:</p>\n"
        twoTabs = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        for promo in promoList:
            htmlStr += "<p>" + twoTabs + promo + "</p>\n"
    return htmlStr

######################## Serialization Functions ########################

def serializeList(objList):
    with open(BUFFER_FILE, 'wb') as file:
        pickle.dump(objList, file)

# open function is relative to working directory
def deserializeList():
    with open(BUFFER_FILE, 'rb') as file:
        objList = pickle.load(file)
    return objList

############################### Retailers ###############################

def findAmazonPrice(url):
    page = getHTMLText(url)
    searchResult = getStringRegexResult(page, r"data-asin-price=\"\d*\.\d*", hardException=False)
    if (searchResult != ""):
        return float(searchResult[17:]), []
    searchResult = getStringRegexResult(page, r"priceblock_ourprice\".*<", hardException=False)
    if (searchResult != ""):
        price = getStringRegexResult(searchResult, r"\d+\.\d+")
        return float(price), []
    searchResult = getStringRegexResult(page, r"priceblock_dealprice.*\n.*")
    price = getStringRegexResult(searchResult, r"\d+\.\d+")
    return float(price), []
    

def findWalmartPrice(url):
    page = getHTMLText(url)
    priceContainer = bsClassFindPrice(page, "prod-PriceHero")
    price = getStringRegexResult(priceContainer, r"\d+\.\d+")
    return float(price), []

############################# Tech Retailers ############################
def findBestBuyPrice(url):   # Detects price even if sold out
    page = getHTMLText(url, requestLibPath=True)
    priceContainer = bsClassFindPrice(page, "priceView-hero-price priceView-customer-price")
    price = getStringRegexResult(priceContainer, r"\d*\.\d*")
    return float(price), []
    
def findBHPhotoPrice(url):
    page = getHTMLText(url)
    price = getStringRegexResult(page, r"pricingPrice.*?\d*\.\d*")
    price = price[15:]
    # Extract coupon container with regex
    couponStr = getStringRegexResult(page, "savingCouponContainer.*?</div", hardException=False)
    if (couponStr != ""):
        # Extract coupon description from container and kick out the framing characters
        regResult = getStringRegexResult(couponStr, "g>.*</d")
        if (regResult != ""):
            return price, [regResult[2:-3]]
    return float(price), []

def findNeweggPrice(url):
    page = getHTMLText(url)
    price = getStringRegexResult(page, r"product_sale_price.*?\d*\.\d*")
    return float(price[21:]), []

############################ Music Retailers ############################
# GuitarCenter
def findGuitarCenterPrice(url):
    page = getHTMLText(url)   # Get page
    # Get 2 line regex result for topAlignedPrice class (easier than BS extraction)
    searchResult = getStringRegexResult(page, r"topAlignedPrice.*\n.*")
    return float(getStringRegexResult(searchResult, r"\d*\.\d*")), []   # Extract price number from topAlignedPrice class

# Musicians Friend
def findMusiciansFriendPrice(url):
    page = getHTMLText(url)
    parsedPage = BeautifulSoup(page, 'html.parser')
    skuDetails = parsedPage.find(id="skuDetail")
    if (skuDetails == None):
        #dumpPageToLog(page, mf)
        raise Exception("Failed to find MF SKU details")
    searchResult = getStringRegexResult(skuDetails.get_text(), r"salePrice=\d*.\d*")
    return float(searchResult[10:]), []

# Sweet Water
def findSweetwaterPrice(url):
    page = getHTMLText(url)
    parsedPage = BeautifulSoup(page, 'html.parser')
    # Extract the price
    priceProp = parsedPage.find(property="product:price:amount")
    if (priceProp == None):
        raise Exception("Price property not found for Sweetwater")
    price = getStringRegexResult(str(priceProp), r"\d+\.\d+")
    
    # Search for promos
    promoStrList = []
    promoClass = parsedPage.find_all("div", class_="product-promo__body")
    if (len(promoClass) != 0):
        for newPromoStr in promoClass:
            promoStrList.append(newPromoStr.contents[0].strip())
    return float(price), promoStrList

URL_PROCESSOR_MAPPER = {"amazon":           findAmazonPrice,
                        "bestbuy":          findBestBuyPrice,
                        "bhphoto":          findBHPhotoPrice,
                        "guitarcenter":     findGuitarCenterPrice,
                        "musiciansfriend":  findMusiciansFriendPrice,
                        "newegg":           findNeweggPrice,
                        "sweetwater":       findSweetwaterPrice,
                        "walmart":          findWalmartPrice}