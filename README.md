# Raspberry Pi Price Scraper
## _Overview_
This is a Python program designed to run regularly on a Raspberry Pi to scrape prices from retailers like Amazon, Best Buy, BHPhoto, Guitar Center, Musicians Friend, Newegg, Sweetwater, and Walmart. Nothing about the code is Pi specific, but the detection appears to be a bit different with a Pi versus something else. Having said that, I expect to have to change methods at some point due to these retailers changing detection methods.
## _Theory of Operation_
The program works by downloading a particular website's raw HTML and parsing it via the html tags or a regex with the intent of grabbing the current price and/or promotions. Both regexes and HTML tags were determined by manually looking through the raw HTML of different retailer entries. A list of products and each product's links are maintain via a buffer file that is used to store the price information and URLs. If the new prices for a particular link are lower than a given percent significance (by default a 3% discount), an email will be sent with the previous and new price along with the hyperlinked URL. The email will include the full list of price changes across the full product list as well as any potential errors encountered.

*Note: The program was initially developed on Python 3.7.3*

__General Flow:__
 - Load the buffer file
 - Download the html page, parse the page, and update each product
 - Check if there was a price drop
   - If not, the program ends without sending an email
 - Build the email text in a partial HTML format
 - Obtain the email credentials in a file located in a separate directory
 - Send the email

*Note: The program checks if there was a change while building the email*
***
# Quick-ish Setup 
_For Beginners: For a more complete explanation of setup and various Python concepts used, see Complete_Installation.md and Python_Concepts.md_

1. Install the following Python libraries with pip
   - requests (should include urllib3 and requests in installation)
   - beautifulsoup4
2. Download or checkout the project package
3. Create a file containing the credentials for a spare email in the directory immediately above the project folder (or where you want) with the name "emailCreds.txt" in the format below:
    ```
    FROM_EMAIL: user@gmail.com
    PASS: P4ssw0rd!
    TO_EMAIL: your@gmail.com
    ```
    _Note: The code currently only supports a gmail sender but can probably be easily modified._
4. Check and update the BUFFER_FILE and EMAIL_FILE paths in "scraperUtilities.py"
5. Run "python scraper.py" to start the interface of adding products and links
   - (Recommended) Create a text file in the format below to quickly populate the object list and run "ingestFileList" inside the interface
    ```
    "product" https://www.bestbuy.com/stuff
    "product" https://www.walmart.com/stuff
    "another product" https://www.walmart.com/another-product
    ```
6. Run "testEmail" as well to validate your email settings in the interface
7. Add program to scheduling by running "crontab -e" and editing the file similar to below:
    ```
    # m h dom mon dow command
    10 12 * * * python3 ~/Desktop/pi-price-scraper/scraper.py updatePrices
    10 0 * * * python3 ~/Desktop/pi-price-scraper/scraper.py updatePrices
    ```
8. Keep your Pi on and reap the benefits