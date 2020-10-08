from scraperUtilities import changeFileName, getHTMLRetailerEntry, getHTMLRetailerPromo, URL_PROCESSOR_MAPPER
from urllib import error
from os.path import isfile
import re


EMAIL_FILE = "../emailCreds.txt"
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
EMAIL_RECEIVER = ""

LINK_IND = 0
PREV_PRICE_IND = 1
CHANGED_PRICE_IND = 2
PREV_PROMO_LIST_IND = 3
NEW_PROMO_LIST_IND = 4

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
                    retailerAndPrice = "  " + retailer.capitalize() + " @ $" + str(self.urlDict[retailer][PREV_PRICE_IND])
                    print(retailerAndPrice + " - " + self.urlDict[retailer][LINK_IND])

    def updatePrices(self):
        for retailer in VALID_RETAILERS:
            retailerList = self.urlDict.get(retailer)
            if (retailerList == None):
                continue
                         
            link = retailerList[LINK_IND]
            try:
                resultList = URL_PROCESSOR_MAPPER[retailer](link)
                newPrice = resultList[0]
                # Store the just parsed promo in the new promo slot to later compare to prevPromo
                self.urlDict[retailer][NEW_PROMO_LIST_IND] = resultList[1]
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
            #print("Diff for " + self.productName + " at " + retailer + " is " + str(percentDiff))
            if (percentDiff > self.significantPercentChange):
                self.urlDict[retailer][CHANGED_PRICE_IND] = newPrice
            #print(str(self.urlDict[retailer][CHANGED_PRICE_IND]))
        return

    def getChangeString(self):
        changeString = ""
        for retailer in VALID_RETAILERS:
            retailerEntryList = self.urlDict.get(retailer)
            if (retailerEntryList == None):
                continue

            prevPromoList = retailerEntryList[PREV_PROMO_LIST_IND]
            newPromoList = retailerEntryList[NEW_PROMO_LIST_IND]
            # If the promos differ, update the previous list to be the new one
            if (newPromoList != prevPromoList):
                self.urlDict[retailer][PREV_PRICE_IND] = newPromoList
            if (retailerEntryList[CHANGED_PRICE_IND] != -1):
                #tempStr = "\t{}:\tThe price decreased from ${:.2f} to ${:.2f} at {}\n"
                prevPrice = "{:.2f}".format(retailerEntryList[PREV_PRICE_IND])
                newPrice = "{:.2f}".format(retailerEntryList[CHANGED_PRICE_IND])
                link = retailerEntryList[LINK_IND]
                #tempStr = "\t{}:\tThe price decreased from $".format(retailer.capitalize())
                #tempStr += "{:.2f} to ${:.2f} at {}\n".format(prevPrice, newPrice, link)
                changeString += getHTMLRetailerEntry(retailer, link, prevPrice, newPrice)
                retailerEntryList[PREV_PRICE_IND] = retailerEntryList[CHANGED_PRICE_IND]
                retailerEntryList[CHANGED_PRICE_IND] = -1

                # If there was not a promo already and if the new promolist isn't empty
                if (newPromoList != []):
                    changeString += getHTMLRetailerPromo(newPromoList) 
            elif (newPromoList != []):
                changeString += getHTMLRetailerPromo(newPromoList, retailer, retailerEntryList[LINK_IND])
        
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
        except error.HTTPError:
            print("\nThe " + retailer + " link is either invalid or unavailable!")
            print("This link was not added.")
            return
        except Exception as e:
            print("\nAnother error occurred. The retailer may be detecting you as a bot.")
            print("This link was not added.")
            print(e)
            return
        retailerEntryList = {retailer : [url, price, -1, promoList, promoList]}
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

    # Intended for use of testing, not normal use
    def resetValueToDefault(self):
        for retailer in VALID_RETAILERS:
            retailerEntryList = self.urlDict.get(retailer)
            if (retailerEntryList == None):
                continue
            self.urlDict[retailer][PREV_PRICE_IND] = 100000.0
            self.urlDict[retailer][PREV_PROMO_LIST_IND] = []
            self.urlDict[retailer][NEW_PROMO_LIST_IND] = []