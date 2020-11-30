from scraperUtilities import changeFileName, getHTMLRetailerEntry, getHTMLRetailerPromo, URL_PROCESSOR_MAPPER
from os.path import isfile
from urllib import error
import re

#############################################
### Index macros for retailer entry lists ###
#############################################
LINK_IND = 0                              ###
PREV_PRICE_IND = 1                        ###
CHANGED_PRICE_IND = 2                     ###
PREV_PROMO_LIST_IND = 3                   ###
NEW_PROMO_LIST_IND = 4                    ###
#############################################

### Comparison tuple for validating retailer during retailer addition ###
VALID_RETAILERS = ("amazon", "bestbuy", "bhphoto", "guitarcenter", "musiciansfriend", "newegg", "sweetwater", "walmart")


class ProductObj:
    # Static class variables
    significantPercentChange = 0.03

    # Constructor
    def __init__(self, name, linkList = []):
        # Instance variables
        self.productName = name
        self.urlDict = {}
        self.errorLog = ""

        if (len(linkList) > 0):
            for url in linkList:
                self.addRetailerLink(url)
    ################# End Function #################

    # Object conversion to string for prints
    def __str__(self):
        return(f"Product Name: {self.productName}\n" + str(self.urlDict))
    ################# End Function #################

    # Print product name of current object and potentially links for each retailer
    def printItems(self, listAllLinks=False):
        print(self.productName)
        if (listAllLinks):
            for i in range(len(VALID_RETAILERS)):
                retailer = VALID_RETAILERS[i]
                # Print if the retailer is in the product url list
                if (retailer in self.urlDict):
                    retailerAndPrice = "  " + retailer.capitalize() + " @ $" + str(self.urlDict[retailer][PREV_PRICE_IND])
                    print(retailerAndPrice + " - " + self.urlDict[retailer][LINK_IND])
    ################# End Function #################

    # Obtain the new prices and process the existing retailer list for the product
    def updatePrices(self):
        for retailer in VALID_RETAILERS:
            retailerList = self.urlDict.get(retailer)
            # Skip the retailer if the retailer is not in the current product's list
            if (retailerList == None):
                continue
            
            # Retrieve link from product
            link = retailerList[LINK_IND]
            # Attempt to successfully obtain the new price and promo list
            try:
                # Run the download and parsing function for the current retailer
                newPrice, promoList = URL_PROCESSOR_MAPPER[retailer](link)
                # Store the just parsed promo in the new promo slot to later compare to prevPromo
                self.urlDict[retailer][NEW_PROMO_LIST_IND] = promoList
            except error.HTTPError as e:
                self.errorLog += "The " + retailer + " link for " + self.productName \
                              + " failed to download or encountered another HTTP related error.\n"
                self.errorLog += str(e) + "\n"
                continue
            # Note the error and dump the HTML or source string to file
            except Exception as e:
                prodNameUnderScored = self.productName.replace(" ", "_")
                # Append the product name and retailer to default "errorDump.html" error file
                fileName = retailer + "-" + prodNameUnderScored + "-" + "errorDump.html"
                changeFileName("errorDump.html", fileName)
                # Add to error log
                self.errorLog += str(e) + "\n"
                continue

            # Compare new price to old price
            prevPrice = self.urlDict[retailer][PREV_PRICE_IND]
            percentDiff = (prevPrice - newPrice) / prevPrice
            # Update new price entry if drop is greater than significant change (default of 3%)
            if (percentDiff > self.significantPercentChange):
                self.urlDict[retailer][CHANGED_PRICE_IND] = newPrice
        return
    ################# End Function #################

    def getChangeString(self):
        changeString = ""
        for retailer in VALID_RETAILERS:
            retailerEntryList = self.urlDict.get(retailer)
            # Skip retailer if not in list
            if (retailerEntryList == None):
                continue

            prevPromoList = retailerEntryList[PREV_PROMO_LIST_IND]
            newPromoList = retailerEntryList[NEW_PROMO_LIST_IND]
            # If the promos differ, update the previous list to be the new one
            if (newPromoList != prevPromoList):
                self.urlDict[retailer][PREV_PRICE_IND] = newPromoList
            # If the new price entry is not the default, begin building string for retailer
            if (retailerEntryList[CHANGED_PRICE_IND] != -1):
                prevPrice = "{:.2f}".format(retailerEntryList[PREV_PRICE_IND])
                newPrice = "{:.2f}".format(retailerEntryList[CHANGED_PRICE_IND])
                link = retailerEntryList[LINK_IND]
                # Append combined product information for retailer entry onto changeString
                changeString += getHTMLRetailerEntry(retailer, link, prevPrice, newPrice)
                # Update previous price with new price
                retailerEntryList[PREV_PRICE_IND] = retailerEntryList[CHANGED_PRICE_IND]
                # Reset the new price to the default
                retailerEntryList[CHANGED_PRICE_IND] = -1

                # If there was not a promo already and if the new promolist isn't empty
                if (newPromoList != []):
                    changeString += getHTMLRetailerPromo(newPromoList) 
            # Construct retailer entry for promo list even if price didn't change
            elif (newPromoList != []):
                changeString += getHTMLRetailerPromo(newPromoList, retailer, retailerEntryList[LINK_IND])
        
        return changeString
    ################# End Function #################

    # Add individual retailer entry to product
    def addRetailerLink(self, url):
        # Divide link into https, retailer domain, and remaining path
        linkSplit = re.split(r"\.", url)

        # Check for valid url format
        if (len(linkSplit) < 3):
            print("Link provided is invalid!\nIt must be a standard https url.")
            return -1
        
        retailer = linkSplit[1]

        if retailer not in VALID_RETAILERS:
            print(f"{linkSplit[1]} is not a valid retailer!")
            return -1

        # Ask if the user wants to replace an existing retailer entry
        if retailer in self.urlDict:
            print(f"The {retailer} retailer is already added to this product!")
            print(f"The current link is:\n{self.urlDict[retailer][LINK_IND]}\n")
            answer = ""
            while (answer != "y"):
                answer = input("Do you want to replace the current link? [y/n]\n").lower()
                if (answer == "n"):
                    print("The new link was not added!")
                    return -1

        # Attempt a successful retailer info retrieval for initial data
        try:
            price, promoList = URL_PROCESSOR_MAPPER[retailer](url)
        # Account for potential URL related errors
        except error.HTTPError:
            print("\nThe " + retailer + " link is either invalid or unavailable!")
            print("This link was not added.")
            return
        # Account for potential bot detection or just HTML format change
        except Exception as e:
            print("\nAnother error occurred. The retailer may be detecting you as a bot.")
            print("This link was not added.")
            print(e)
            return
        # Load new entry with obtained data and default data
        retailerEntryList = {retailer : [url, price, -1, promoList, promoList]}
        self.urlDict.update(retailerEntryList)
    ################# End Function #################

    # Remove retailer entry for product
    def removeRetailer(self, retailer):
        if (retailer not in VALID_RETAILERS):
            print("Not a valid retailer")
            return
        
        if (retailer not in self.urlDict):
            print(retailer.capitalize() + " not in {self.productName} list!")
            return

        # Properly remove entry all together from product's url list
        self.urlDict.pop(retailer)
        print("Successfully removed " + retailer + " from " + self.productName)
    ################# End Function #################

    # Intended for use of testing, not normal use
    def resetValueToDefault(self):
        for retailer in VALID_RETAILERS:
            retailerEntryList = self.urlDict.get(retailer)
            # Skip retailer if not in list
            if (retailerEntryList == None):
                continue
            self.urlDict[retailer][PREV_PRICE_IND] = 100000.0
            self.urlDict[retailer][PREV_PROMO_LIST_IND] = []
            self.urlDict[retailer][NEW_PROMO_LIST_IND] = []
    ################# End Function #################