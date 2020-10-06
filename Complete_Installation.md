# Complete Installation and Setup
## _Prior Setup on Main Computer_
1. Create a spare gmail if you do not already have one (not your main account!). This ensures that if the Pi is somehow compromised (very unlikely) that you will not be subject to losing your main email and potentially more.

   - _The code currently only supports a gmail sender (your spare email) but can probably be easily modified to support other providers._
2. Log into your spare gmail account and follow these steps:
   - Go to "Manage your Google Account"
   - Click on the `Security` Tab
   - Scroll down to "Less secure app access" and click `Turn on access (not recommended)`
   - Allowing "Less secure app access" is one of the primary reasons you should use a spare or junk email
3. Amass a list of products and full https URLs/links to any of the supported retailers in a text file formatted in the way as shown below.
    - The "product" name does not have to match the actual product name, but having the same "product" name on multiple lines will allow you to associate that same product with different retailer links.
    - To create the file, you can just use notepad or a similar basic text editor. Save this file to something like `links.txt` or whatever you want. The formatting is more important than the file name.
    ```
    "product" https://www.bestbuy.com/stuff
    "product" https://www.walmart.com/stuff
    "another product" https://www.walmart.com/another-product
    ```
4. Save and move the file to a flash drive or another medium to be able to move it to the Raspberry Pi once it is all set up.
----
## _Setting up the Raspberry Pi_
1. (If not already done) Install and run NOOBS to set up Raspberry Pi OS on the Pi according to the [official](https://www.raspberrypi.org/documentation/installation/) guide or another guide
2. Once it is booted, connect the Pi to the internet and open the command terminal by clicking the icon that looks like a black box or by pressing `Ctrl+Alt+T`
3. Inside the terminal window, run the command below and enter `y` when it asks for confirmation. `sudo` runs the command at an elevated privilege like "Adminstrator Mode" in windows. `apt-get update` gets the update packages from the necessary code repositories, and `apt-get upgrade` will actually install them.
   - `sudo apt-get update && sudo apt-get upgrade` 
   - Note that updating can take a while depending upon how recent your version of NOOBS is...
   - There may be some intermediary prompts showing changelogs and things like that, but just press `q` to get out of them to continue updating. As long as there aren't any major errors, you are good.
4. Run `sudo reboot` once updating finishes without errors
5. Once the pi reboots, bring the terminal back up and run the below command to install the python3 package dependencies
   - `sudo pip3 install beautifulsoup4 requests`
6. Next, follow this sequence of commands. The commands are explained after the code box rather than just making you run them wrote from instruction. You may want to take a peek at the explanations first if you don't feel 100% in your element.
   
    *Note: These commands will result in you installing the program folder to your Pi desktop. You can change the place of installation, but you will need to ensure changing the necessary file paths are changed in the code*
   ```
    pwd
    cd Desktop
    git clone https://github.com/zsholdbrooks/pi-price-scraper.git
    ls
   ```
   - `pwd` - This command prints the working directory (where you are in the linux filesystem)
     - Whenever opening a new terminal, you generally will start at the current user's home directory denoted by the `~` symbol
   - `cd Desktop` - cd is for "change directory" allowing you to move around the file system by changing your current directory/folder (thus changing your `pwd` output as well as the path shown just before the `$` on the prompt)
     - Tip: If you are wanting to not type a full directory, hitting `Tab` will give you either partial or full autocompletion in most terminals. Hitting `Tab` twice shows you a list of files available from the current partial pattern.
     - This tip is the same as running `ls stuff*` if you have multiple files starting with the string `stuff` like `stuff1.txt` and `stuff2.txt`
   - `git clone <link>` - This command will attempt to download the git repository into the current directory. The link in the code box sequence is the link to the root of this code repository where it shows all the files. This command is also equivalent to downloading the code as a ZIP and unpackaging it somewhere.
   - `ls` - This command shows the files (most of them) in your current directory. Note that after running the `git clone` command, the "pi-price-scraper" folder pops up on your Desktop as well as in the terminal after running `ls`
7. Create a file containing the credentials for the spare email by running the command below and following the instructions below
    - `nano emailCreds.txt`
    - Type out your spare email, spare email password, and intended email target (probably your main email as the TO_EMAIL) in the format shown below
        ```
        FROM_EMAIL: user@gmail.com
        PASS: P4ssw0rd!
        TO_EMAIL: your@gmail.com
        ```
    - Once you are done, press `Ctrl+X` to begin to exit, press `Y` to confirm, and `Enter` to accept the name you typed in already with the initial command
    
8.  Run `cd /home/pi/Desktop/pi-price-scraper` to enter the project folder
    - If you get a `No such file or directory` error then do the next step. If you are successfully in the project folder, skip to the **Watchlist Setup**
9.  (Optional) **Skip this if your user is the default "pi" and you installed the project on the Desktop. English: If you are strictly following this guide, you can likely skip this.**
    - If you install the project in another location other than the Desktop, update the BUFFER_FILE and EMAIL_FILE path variables in the `scraperUtilities.py` file. This is due to how crontab will interpret the file paths since it is running from a different working directory from the project directory.

## _Watchlist Setup_
1. Drag and drop that `links.txt` file you created earlier into the pi-price-scraper folder
2. Run the following command to begin setting up your watchlist. It will launch the program's interface.
    - `python3 scraper.py`
3. Enter in `ingestFileList` when it asks for a command
4. Enter in the name of the file containing all your links. You would type in `links.txt` if you are following this guide to the letter.
5. Watch the output and make sure it doesn't encounter any errors. It may ask you to respond to potential link duplicates if it detects them. Otherwise, it should parse them without extra input.
6. Once the parsing is successful, run `listAllLinks` to make sure that all of your products and links have been added correctly.
7. Run `testEmail` as well to validate your email settings in the interface
    - You should receive a sample email on your TO_EMAIL account pretty shortly if all goes well. If not, make sure you followed the format shown above.

_Note: If you need to start editing or removing items, just rerun `python3 scraper.py` inside the project folder to start using the interface to interact with your watch list._

## _Setting Up Scheduling_
To make sure the program runs regularly, we will use an already installed program called "crontab" that will run the program at set intervals. The guide will show the two interval times being set to run the program at 12:10 AM and 12:10 PM daily. Look a bit more into crontab to change the interval times.

1. Run the below command to begin editing the scheduling file
   - `crontab -e`
2. If this is the first time crontab starts, it will ask for an editor. Nano will be the easiest to use.
   - Type `1` and hit `Enter` to select "nano" as your editor like before.
3. Once it launches into the file, hold the `Down Arrow Key` to reach the bottom of the file.
4. Type in the following two lines at the very bottom of the file.
   - _Note: The part of the two lines after `updatePrices` is Linux syntax for dumping errors into a file within the project folder since you will be unable to see direct output from the scheduled commands._
    ```
    10 12 * * * python3 ~/Desktop/pi-price-scraper/scraper.py updatePrices >> ~/Desktop/pi-price-scraper/cron-error.log 2>&1
    10 0 * * * python3 ~/Desktop/pi-price-scraper/scraper.py updatePrices >> ~/Desktop/pi-price-scraper/cron-error.log 2>&1
    ```
5.  Once you are done typing in the two lines, press `Ctrl+X` to begin to exit, press `Y` to confirm, and `Enter` to exit the file.
6.  You are now done (hopefully with no errors) with setup and will receive an email at either of the two scheduled times if the program detects a price drop.


***
# Setting Up VSCode for Remote Development
*__Caution: This set of instructions will generally be more for those who are interested more in actual independent development on the Raspberry Pi.__*

*__Important Note: Microsoft apparently does not yet support the ARMv6 architecture in their SSH extension. Because of this, you cannot use this guide if you have a Raspberry Pi Zero W (and probably the Raspberry Pi 1).__*

Going this route will inevitably require regular usage of the command line, so many may be uncomfortable or unwilling to run down this path. I would honestly recommend it for everyone, but I can see very many getting lost in the steps and this process not being worth some people's time given their singular use.

As an aside, I love this workflow because it allows me to have my Raspberry Pi running with just a power and Wi-Fi connection while still being able to develop on either my laptop or desktop. This gives me the ease and speed of working on a Windows or Mac system (with one KB and mouse set) while being able to target the Raspberry Pi. VS Code also stands to me to be the best utility for development due to its near universal support of languages. While it may not have more targeted tools like VS Community and the likes of PyCharm, it is very good at being leveraged for a variety of tasks.

## _Setup on the Pi_

1. Install openssh-server on the Pi by running the command below
   - `sudo apt-get install openssh-server`
   - It's possible it is already installed.
2. Run the following commands to enable the ssh server service and start it
   - `sudo systemctl enable ssh`
   - `sudo systemctl start ssh`
3. Run the command below to obtain your Pi's IP address
   - `hostname -I`
4. To find out your user name, run the commmand below
   - `whoami`
5. After finding both your user name and your IP address, make sure to note or write down these two in the following format
   - `ssh user@ipAddress`
   - If you have a default setup, this pattern will likely be something like `ssh pi@192.168.*.*` where `*` is any positive number below 256

Now that you have the ssh server enabled and started, it should remain on and even start back up after a reboot of the Pi.

## _Setup on your Main Computer_
This part essentially follows a simplified version of [Microsoft's guide](https://code.visualstudio.com/docs/remote/ssh-tutorial).
1.  Download and install VS Code from [Microsoft's website](https://code.visualstudio.com/)
2.  Open VS Code and install Microsoft's [Remote development extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)
       - You can click the link, click `Install`, and follow the prompts to open up the app page within VS Code
3.  Once the extension is installed and VS Code restarts, click on the icon on the far left toolbar that looks like a computer monitor
       - If you are having trouble locating the specific icon, hover over each one until you find the one that is the `Remote Explorer`
4.  Once there, you will see a section to the right of the icon with the name `SSH Targets`. Hover over that section until you locate the `+`, settings gear, and refresh symbol right next to the `SSH TARGETS` title. Click on the `+` symbol to add a new ssh target.
5.  Now VS Code will prompt you with a prompt box that has a command example with a very familiar format. Type in the `ssh user@ipAddress` command that you noted earlier in the Pi Setup and hit `Enter`.
6.  When it asks for the `SSH configuration file to update`, just hit `Enter`
7.  Click on the new IP entry in the SSH Targets tab and click the folder (maybe a terminal window?) looking icon. This launches a new window with a VS Code workspace that is inside the Raspberry Pi. This will be how you "log into the Pi" whenever you want to get on it to start doing development.
8.  When you open the SSH Target, select `Linux`, select `Yes`, and enter in the password for your Raspberry Pi.
9.  Once it is properly connected, click the `Terminal` tab at the top and select `New Terminal`. This will start up your terminal for your Pi. This terminal acts the exact same as if you were running commands on the terminal on the Pi directly.
10. (Optional) You are now done with setup, but you can actually rename your Raspberry Pi target from the IP address to a proper name.
    - To do this, click the settings gear icon by the `SSH TARGETS` heading to open the SSH configuration file.
    - Click the first file (assuming that was the SSH config file you used during setup).
    - Then change `Host` to be your desired name with no spaces like `RaspberryPi` or `Raspberry_Pi`.

# Known issues
- Running "scraper.py" causes an error in scraperClass.py with a return statement that has an `f` before the string.
  - This is due to not having the latest python3 version. Run `python3 -V` and note the lower version than 3.6 when string formatting changed a bit.
  - I would recommend upgrading to the latest version of python3 if you want to use this program. There are other pieces regarding the creation of the buffer file that are python version dependent as well. Upgrading may break other programs due to issues of compatibility. I don't know. It all depends.
  - If you seem to be stuck in python 3.5.3 or another variant well below the latest, it is possible you are still on Rasbian rather than Raspberry Pi OS. I had this issue myself, and while it is possible to upgrade an existing copy of Raspbian, it appears to be easier to start with a clean new install.