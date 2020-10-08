from scraperClass import ProductObj
from scraperUtilities import BUFFER_FILE, deserializeList, serializeList, getStringRegexResult, getEmailCreds, sendEmail
from sys import argv
from os.path import isfile

########################## Global Product List #########################
ObjList = []    # Loaded by running deserializeList() to retrieve list from cached file

###################### Program Interface Commands ######################
VALID_COMMANDS = {"additem", "ingestfilelist", "edititem", "removeitem", \
                  "listallitems", "listalllinks", "testemail", "resetvalues"}

########################################################################
########################### Utility Functions ##########################
########################################################################

def buildAndSendEmail():
    # Retrieve email info
    sender, sender_password, receiver = getEmailCreds()
    emailBody = ""
    errorBody = ""

    # Iterate for each product
    for obj in ObjList:
        # Obtain updated product info string
        newChangeStr = obj.getChangeString()

        # Append errors for current product if they are detected during processing
        if (obj.errorLog != ""):
            errorBody += obj.errorLog  # Add collected errors to email error section
            obj.errorLog = ""   # Reset objects error log to default empty string

        # Continue to next product if object signals no promo or price updates
        if (newChangeStr == ""):
            continue

        # Create email product header
        emailBody += "<p><b>" + obj.productName + ":</b></p>\n"
        # Add changed info to email body
        emailBody += newChangeStr + "\n"

    # Add errors to end of email if any exist
    if (errorBody != ""):
        emailBody += "\nErrors:\n" + errorBody
    
    # Skip sending email if there are neither errors or updates
    if (emailBody == ""):
        print("No email sent!")
        return

    sendEmail(sender, sender_password, receiver, emailBody)
    ################# End Function #################

def extractQuote(strCmd):
    strList = strCmd.split('"')
    # Obtain substring just after first " mark if there is a set of quotation marks
    if (len(strList) > 1):
        return strList[1].strip()
    return ""
    ################# End Function #################

def findProductIndexInList(targetName):
    for i in range(len(ObjList)):
        if (ObjList[i].productName == targetName):
            return i
    return -1
    ################# End Function #################

def printTopLevelCommands():
    print("Available commands:")
    print("  addItem \"item\"")
    print("  ingestFileList")
    print("  editItem")
    print("  removeItem")
    print("  listAllItems")
    print("  listAllLinks")
    print("  testEmail")
    print("Note: 'addItem' can be run without arguments to enter manual interface.")
    ################# End Function #################

def processCommand(cmdStr, cmdFirstArg = ""):
    if (cmdFirstArg == ""):
        cmdFirstArg = getStringRegexResult(cmdStr, r"\S*").lower()
    
    if (cmdFirstArg not in VALID_COMMANDS):
        print("Invalid Command!\n")
        printTopLevelCommands()
        return

    if (cmdFirstArg == "additem"):
        addItem(cmdStr)
    if (cmdFirstArg == "ingestfilelist"):
        ingestFileList()
    elif (cmdFirstArg == "edititem"):
        editItem()
    elif (cmdFirstArg == "removeitem"):
        removeItem()
    elif (cmdFirstArg == "testemail"):
        testEmail()
    elif (cmdFirstArg == "resetvalues"):
        forceValuesToDefault()
    else:
        listAllLinks = (cmdFirstArg == "listalllinks")
        listEntries(listAllLinks)
    ################# End Function #################

##### Provides a list of current objects in ObjList to choose from #####
def selectItemFromList():
    itemIndex = None
    while (itemIndex not in range(len(ObjList) + 1)):
        for i in range(len(ObjList)):
            print(str(i + 1) + " - " + ObjList[i].productName)
        rawInput = input("\nEnter the desired index or 0 to quit: ")
        # Attempt to get valid integer number
        try:
            itemIndex = int(rawInput)
        # Use -1 as default if input can't be properly converted
        except:
            itemIndex = -1
    # Convert back to 0 based indexing from displayed list's starting number of 1
    return itemIndex - 1
    ################# End Function #################

########################################################################
########################### Command Functions ##########################
########################################################################

def addItem(cmdStr):
    productName = ""
    urlList = []
    cmdArgList = cmdStr.split(" ")[1:]

    # Attempt to parse product name straight from command
    if (len(cmdArgList) > 0):
        productName = extractQuote(cmdStr).strip()
    # Otherwise, prompt for the name directly
    if (productName == ""):
        productName = input("Product name (without quotes)? ").strip()

    if (findProductIndexInList(productName) != -1):
        print("This product is already in the watch list!")
        print("Attempt to edit this item to add links.")
        return

    print("Paste and enter individual links!")
    potentialLink = input("Enter a new link or 'q' to quit adding links: ")
    while (potentialLink != "q"):
        urlList.append(potentialLink)
        potentialLink = input("Enter a new link or 'q' to quit adding links: ")
        
    if (len(urlList) == 0):
        print("No links will be added, but the product will be added to the list")
    # Create new product container with the obtained link list
    newObj = ProductObj(name=productName, linkList=urlList)
    # Add the new product to the list so that it can be cached
    ObjList.append(newObj)
    return
    ################# End Function #################

def editItem():
    # Select product from displayed list
    itemIndex = selectItemFromList()
    if (itemIndex == -1):
        return

    currObj = ObjList[itemIndex]
    
    cmd = ""    # Display interface at start with default command
    cmdList = cmd.split(" ")
    while cmdList[0] not in ("q", "quit"):
        # Add new link with new url
        if (cmdList[0] == "addlink"):
            # Check a second argument was passed
            if (len(cmdList) != 2):
                print("Invalid addLink command")
            else:
                newLink = cmdList[1]
                currObj.addRetailerLink(newLink)
        # Display all links associated with current product
        elif (cmdList[0] == "listlinks"):
            currObj.printItems(listAllLinks=True)
        # Remove a specific link by specifying a valid retailer
        elif (cmdList[0] == "removelink"):
            if (len(cmdList) != 2):
                print("Invalid removeLink command")
            else:
                retailer = cmdList[1].lower()
                currObj.removeRetailer(retailer)
        # Display available commands if invalid command is used
        else:
            print("Available commands:")
            print("  addLink <single https link>")
            print("  removeLink <retailer i.e amazon>")
            print("  listlinks")
        
        cmd = input("\nNext edit command? ")
        cmdList = cmd.split(" ")
        cmdList[0] = cmdList[0].lower()
    ################# End Function #################

######## Print the list of current objects ########
def listEntries(listAllLinks=False):
    if (len(ObjList) == 0):
        print("The current item list is empty!")
    else:
        for obj in ObjList:
            obj.printItems(listAllLinks)
    ################# End Function #################

# Remove a product in the list and all its links
def removeItem():
    itemIndex = selectItemFromList()
    if (itemIndex == -1):
        return

    # Delete entry from list so that the change is cached later
    del ObjList[itemIndex]
    ################# End Function #################

# Take in a list of products and urls to add to the current list
def ingestFileList():
    fileName = input("Input file name: ")

    # Exit if specified file is not found
    if (not isfile(fileName)):
        print("Error: Not a valid file!")
        return
    # Begin parsing through file
    else:
        with open(fileName, "r") as file:
            # Load all entries within the file
            lineList = file.readlines()
            if (len(lineList) == 0):
                print("Empty file!")
                return
            
            for line in lineList:
                # Attempt to successfully grab parameters from current line
                try:
                    prodName = getStringRegexResult(line, r'".*"')[1:-1]
                    link = getStringRegexResult(line, r'\bhttps.*\b')
                # Report that the line was not added successfully if parameters
                # are not in expected format
                except:
                    print("Error adding line: " + line)
                    continue
                # Attempt to find the same product name in the existing product list
                objIndex = findProductIndexInList(prodName)
                # Add the link to the existing product
                if (objIndex != -1):
                    ObjList[objIndex].addRetailerLink(link)
                # Otherwise, create a new product object with the obtained link
                else:
                    newObj = ProductObj(prodName, [link])
                    ObjList.append(newObj)

        print("Finished ingesting " + fileName)
    ################# End Function #################

########################################################################
########################### Tester Functions ###########################
########################################################################

# Test email for valid EMAIL_FILE settings and proper email server settings
def testEmail():
    sender, sender_password, receiver = getEmailCreds()
    mailtext = "Well, your email connection appears to be working!"

    sendEmail(sender, sender_password, receiver, mailtext)
    ################# End Function #################

# This command is intentionally hidden from listed commands for testing
# Not necessary for normal use (hence why it is hidden)
def forceValuesToDefault():
    if (ObjList == []):
        print("List is empty!")
        return
    else:
        for obj in ObjList:
            obj.resetValueToDefault()
        print("Values have been reset!")
    ################# End Function #################

########################################################################
########################## Interface Functions #########################
########################################################################

# Function used for auto-updating object list
def processList():
    # Check that the ObjList was obtained successfully or is not empty
    if (ObjList == []):
        print("Failed to process the objects because the list is empty")
        return

    # Run processing and fetching
    for obj in ObjList:
        obj.updatePrices()

    # Grab all of the changed and send email if there has been a change
    buildAndSendEmail()
    # Serialize the ObjList back to buffer file in main function after returning
    ################# End Function #################

def progInterface():
    cmdStr = cmdFirstArg = ""
    # Main interface input loop
    while cmdFirstArg not in ("q", "quit"):
        if cmdFirstArg in ("", "h", "help"):
            printTopLevelCommands()
        else:
            processCommand(cmdStr, cmdFirstArg)
        
        cmdStr = input("\nNext menu command? ").strip()
        cmdFirstArg = getStringRegexResult(cmdStr, r"\S*").lower()
    ################# End Function #################

########################################################################
############################ Main Function #############################
########################################################################

if __name__ == "__main__":
    # Attempt to load Product list from cached file
    if (isfile(BUFFER_FILE)):
        print("Loading existing list")
        ObjList = deserializeList()

    # Open interface if script is run without arguments
    if (len(argv) == 1):
        progInterface()
    # Run automatic updating
    elif (argv[1] == "updatePrices"):
        processList()
    # Otherwise, run one of the in built interface commands direct from CLI
    else:
        processCommand(argv)

    # Save edited object information
    serializeList(ObjList)