from scraperClass import ProductObj
from scraperUtilities import BUFFER_FILE, deserializeList, serializeList, getStringRegexResult, getEmailCreds, sendEmail
from sys import argv
from os.path import isfile

ObjList = []
VALID_COMMANDS = {"additem", "ingestfilelist", "edititem", "removeitem", "listallitems", "listalllinks", "testemail", "resetvalues"}

########################################################################
########################### Utility Functions ##########################
########################################################################
def buildAndSendEmail(ObjListLocal):
    sender, sender_password, receiver = getEmailCreds()
    emailBody = ""
    errorBody = ""
    for obj in ObjListLocal:
        newChangeStr = obj.getChangeString()
        if (newChangeStr == ""):
            continue
        emailBody += "<p><b>" + obj.productName + ":</b></p>\n"
        emailBody += newChangeStr + "\n"
        if (obj.errorLog != ""):
            errorBody += obj.errorLog
            obj.errorLog = ""

    if (errorBody != ""):
        emailBody += "\nErrors:\n" + errorBody
    if (emailBody == ""):
        print("No email sent!")
        return
    sendEmail(sender, sender_password, receiver, emailBody)
    #######

def extractQuote(strCmd):
    strList = strCmd.split('"')
    if (len(strList) > 1):
        return strList[1].strip()
    return ""

def findProductIndexInList(targetName):
    for i in range(len(ObjList)):
        if (ObjList[i].productName == targetName):
            return i
    return -1

def printTopLevelCommands():
    print("Available commands:")
    print("  addItem \"item\"")
    print("  ingestFileList")
    print("  editItem")
    print("  removeItem")
    print("  listAllItems")
    print("  listAllLinks")
    print("  testemail")
    print("Note: 'add' can be run without arguments to enter manual interface.")

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

##### Provides a list of current objects in ObjList to choose from #####
def selectItemFromList():
    itemIndex = None
    while (itemIndex not in range(len(ObjList) + 1)):
        for i in range(len(ObjList)):
            print(str(i + 1) + " - " + ObjList[i].productName)
        rawInput = input("\nEnter the desired index or 0 to quit: ")
        try:
            itemIndex = int(rawInput)
        except:
            itemIndex = -1
    return itemIndex - 1

########################################################################
########################### Command Functions ##########################
########################################################################
def addItem(cmdStr):
    productName = ""
    urlList = []
    cmdArgList = cmdStr.split(" ")[1:]

    if (len(cmdArgList) > 0):
        productName = extractQuote(cmdStr).strip()
    if (productName == ""):
        productName = input("Product name (without quotes)? ").strip()

    if (findProductIndexInList(productName) != -1):
        print("This product is already in the watch list!")
        return

    print("Paste and enter individual links!")
    potentialLink = input("Enter a new link or 'q' to quit adding links: ")
    while (potentialLink != "q"):
        urlList.append(potentialLink)
        potentialLink = input("Enter a new link or 'q' to quit adding links: ")
        
    if (len(urlList) == 0):
        print("No links will be added, but the product will be added to the list")
    newObj = ProductObj(name=productName, linkList=urlList)
    ObjList.append(newObj)
    return

def editItem():
    itemIndex = selectItemFromList()
    if (itemIndex == -1):
        return

    currObj = ObjList[itemIndex]
    
    cmd = ""
    cmdList = cmd.split(" ")
    while cmdList[0] not in ("q", "quit"):
        if (cmdList[0] == "addlink"):
            if (len(cmdList) != 2):
                print("Invalid addLink command")
            else:
                newLink = cmdList[1]
                currObj.addRetailerLink(newLink)
        elif (cmdList[0] == "listlinks"):
            currObj.printItems(listAllLinks=True)
        elif (cmdList[0] == "removelink"):
            if (len(cmdList) != 2):
                print("Invalid removeLink command")
            else:
                retailer = cmdList[1].lower()
                currObj.removeRetailer(retailer)
        else:
            print("Available commands:")
            print("  addLink <single https link>")
            print("  removeLink <retailer i.e amazon>")
            print("  listlinks")
        cmd = input("\nNext edit command? ")
        cmdList = cmd.split(" ")
        cmdList[0] = cmdList[0].lower()

######## Print the list of current objects ########
def listEntries(listAllLinks=False):
    if (len(ObjList) == 0):
        print("The current item list is empty!")
    else:
        for obj in ObjList:
            obj.printItems(listAllLinks)

def removeItem():
    print("remove cmd")
    itemIndex = selectItemFromList()
    if (itemIndex == -1):
        return

    del ObjList[itemIndex]

def ingestFileList():
    fileName = input("Input file name: ")
    if (not isfile(fileName)):
        print("Error: Not a valid file!")
        return
    else:
        with open(fileName, "r") as file:
            lineList = file.readlines()
            if (len(lineList) == 0):
                print("Empty file!")
                return
            
            for line in lineList:
                try:
                    prodName = getStringRegexResult(line, r'".*"')[1:-1]
                    link = getStringRegexResult(line, r'\bhttps.*\b')
                except:
                    print("Error adding line: " + line)
                    continue
                objIndex = findProductIndexInList(prodName)
                if (objIndex != -1): # If product is in list
                    ObjList[objIndex].addRetailerLink(link)
                else:
                    newObj = ProductObj(prodName, [link])
                    ObjList.append(newObj)

        print("Finished ingesting " + fileName)

def testEmail():
    sender, sender_password, receiver = getEmailCreds()
    mailtext = "Well, your email connection appears to be working!"

    sendEmail(sender, sender_password, receiver, mailtext)

# This command is intentionally hidden from listed commands for testing
def forceValuesToDefault():
    if (ObjList == []):
        print("List is empty!")
        return
    else:
        for obj in ObjList:
            obj.resetValueToDefault()
        print("Values have been reset!")

########################################################################
########################## Interface Functions #########################
########################################################################

# run "python3 -c 'import scraper; scraper.processList()'"
def processList():
    # Deserialize the buffer file because it is detached from interface
    if (isfile(BUFFER_FILE)):
        print("Loading existing list")
        ObjList = deserializeList() # Run in isolation as command, it treats ObjList as local var
    else:
        print("Failed to process the objects because there is no buffer file")
        return

    # Run processing and fetching
    for obj in ObjList:
        obj.updatePrices()

    # Grab all of the changed and send email if there has been a change
    buildAndSendEmail(ObjList)
    # Serialize the ObjList back to buffer file
    serializeList(ObjList)

def progInterface():
    cmdStr = cmdFirstArg = ""
    while cmdFirstArg not in ("q", "quit"):
        if cmdFirstArg in ("", "h", "help"):
            printTopLevelCommands()
        else:
            processCommand(cmdStr, cmdFirstArg)
        cmdStr = input("\nNext menu command? ").strip()
        cmdFirstArg = getStringRegexResult(cmdStr, r"\S*").lower()

########################################################################
############################ Main Function #############################
########################################################################

if __name__ == "__main__":
    if (isfile(BUFFER_FILE)):
        print("Loading existing list")
        ObjList = deserializeList()

    if (len(argv) == 1):
        progInterface()
    else:
        processCommand(argv)

    # add if has changed
    serializeList(ObjList)