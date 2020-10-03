from scraperUtilities import changeFileName, URL_PROCESSOR_MAPPER
from os.path import isfile
import re
import urllib


EMAIL_FILE = "../emailCreds.txt"
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
EMAIL_RECEIVER = ""

LINK_IND = 0
PREV_PRICE_IND = 1
CHANGED_PRICE_IND = 2
PROMO_LIST_IND = 3

VALID_RETAILERS = ("amazon", "bestbuy", "bhphoto", "guitarcenter", "musiciansfriend", "newegg", "sweetwater", "walmart")


class ProductObj:
    # Static class variables
    significantPercentChange = 0.03

    def __init__(self, name, linkList = []):
        # Instance variables
        self.productName = name
        self.urlDict = {}
        self.errorLog = ""

        if (len(linkList) > 0):
            for url in linkList:
                self.addRetailerLink(url)

    def __str__(self):
        return(f"Product Name: {self.productName}\n" + str(self.urlDict))

    def printItems(self, listAllLinks=False):
        print(self.productName)
        if (listAllLinks):
            for i in range(len(VALID_RETAILERS)):
                retailer = VALID_RETAILERS[i]
                if (retailer in self.urlDict):
                    print("  " + retailer.capitalize() + " - " + self.urlDict[retailer][LINK_IND])

    def updatePrices(self):
        for retailer in VALID_RETAILERS:
            retailerList = self.urlDict.get(retailer)
            if (retailerList == None):
                continue
                         
            link = retailerList[LINK_IND]
            try:
                resultList = URL_PROCESSOR_MAPPER[retailer](link)
                newPrice = resultList[0]
                self.urlDict[retailer][PROMO_LIST_IND] = resultList[1]
            except Exception as e:
                prodNameUnderScored = self.productName.replace(" ", "_")
                fileName = retailer + "-" + prodNameUnderScored + "-" + "errorDump.html"
                changeFileName("errorDump.html", fileName)
                # Add to error log
                self.errorLog += str(e) + "\n"
                continue

            # Compare new price to old price
            prevPrice = self.urlDict[retailer][PREV_PRICE_IND]
            percentDiff = (prevPrice - newPrice) / prevPrice
            #print("Diff for " self.productName + " at " + retailer + " is " + percentDiff)
            if (percentDiff > self.significantPercentChange):
                self.urlDict[CHANGED_PRICE_IND] = newPrice

        return

    def getChangeString(self):
        changeString = ""
        for retailer in VALID_RETAILERS:
            retailerEntryList = self.urlDict.get(retailer)
            if (retailerEntryList == None):
                continue
            
            if (retailerEntryList[CHANGED_PRICE_IND] != -1):
                tempStr = "\t{}:\tThe price decreased from ${:.2f} to ${:.2f} at {}\n"
                tempStr.format(retailer.capitalize(), retailerEntryList[PREV_PRICE_IND],\
                    retailerEntryList[CHANGED_PRICE_IND], retailerEntryList[LINK_IND])
                changeString += tempStr
                
                promoList = retailerEntryList[PROMO_LIST_IND]
                if (promoList != []):
                    tempStr += "\t\tPromos:\n"
                    for promo in promoList:
                        tempStr += "\t\t  " + promo + "\n"
                    retailerEntryList[PROMO_LIST_IND] = []
                retailerEntryList[PREV_PRICE_IND] = retailerEntryList[CHANGED_PRICE_IND]
                retailerEntryList[CHANGED_PRICE_IND] = -1
        
        return changeString

    def addRetailerLink(self, url):
        linkSplit = re.split(r"\.", url)

        if (len(linkSplit) < 3):
            print("Link provided is invalid!\nIt must be a standard https url.")
            return -1
        
        retailer = linkSplit[1]

        if retailer not in VALID_RETAILERS:
            print(f"{linkSplit[1]} is not a valid retailer!")
            return -1

        if retailer in self.urlDict:
            print(f"The {retailer} retailer is already added to this product!")
            print(f"The current link is:\n{self.urlDict[retailer][LINK_IND]}\n")
            answer = ""
            while (answer != "y"):
                answer = input("Do you want to replace the current link? [y/n]\n").lower()
                if (answer == "n"):
                    print("The new link was not added!")
                    return -1

        try:
            price, promoList = URL_PROCESSOR_MAPPER[retailer](url)
        except urllib.error.HTTPError:
            print("\nThe " + retailer + " link is either invalid or unavailable!")
            print("This link was not added.")
            return
        except Exception as e:
            print("\nAnother error occurred. The retailer may be detecting you as a bot.")
            print("This link was not added.")
            print(e)
            return
        retailerEntryList = {retailer : [url, price, False, promoList]}
        self.urlDict.update(retailerEntryList)

    def removeRetailer(self, retailer):
        if (retailer not in VALID_RETAILERS):
            print("Not a valid retailer")
            return
        
        if (retailer not in self.urlDict):
            print(retailer.capitalize() + " not in {self.productName} list!")
            return

        self.urlDict.pop(retailer)
        print("Successfully removed " + retailer + " from " + self.productName)