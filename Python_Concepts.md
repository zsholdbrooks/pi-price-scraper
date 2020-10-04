# Python Concepts Used
This document isn't intended to be a full tutorial or introduction to syntax and usage of Python but rather an explanation of various usages of techniques I used in this project that I found interesting.

## _Quick Background_
### Object Oriented Programming
- The definition for OOP has been one of intensive discussion amongst the programming community. A practical definition is that is a practice where you, as a programmer, intend to create abstracted objects a class with attributes and methods for a self-contained interface rather than a bunch of connected individual pieces. 
### What's a class?
- Umm, what? Yeah, so let's use a ball for an example. Most balls have very similar properties like color, sizes, textures, weights, etc. You can use this knowledge to use classes as something of a unifying template.
- They also usually have common actions as well and can group them as methods. But don't certain balls have certain rules in certain circumstances? Yeah, you can actually emulate this with inheritance in OOP where you extend the class to make it already have the same attributes and methods as a general ball while adding new attributes and constraints.
- Usually using classes, you end up with some form of denotation to use an individual objects attributes and methods.
  - You usually declare new instances like `Ball myNewBall = Ball()` where Ball is the class name and Ball() is the constructor that will create the new instance
  - For attributes, you might have `myNewBall.color = "brown"` represent myNewBall's color while you can have another ball like `anotherBall.color = "white"` thus illustrating the difference between a class and an instance of the class
  - For methods, the usage is very similar resulting in like `myNewBall.kick()` where the parentheses usually denote a function implemented in the Ball class. These can also take more variables to do different things or interact with myNewBall's other attributes independent of other class instances.
  - There are also types of attributes and methods such as public, protected, and private types, but that is beyond the scope of this discussion and not used in this code.

### Notes on Arrays and Lists
Arrays and lists in python use 0-based integer index denotation. This means that a list or array, assuming it is not empty, can be accessed with the first entry index starting with 0 and the last one being the total number of entries minus 1 like `myList[0]` and `myArray[len(myArray) - 1]`. Python also supports negative indexes and slicing/subsection selection.

Examples:
```
    myList[0]
    myArray[len(myArray) - 1]
    # Everything from the third index to the end
    myList[2:]
    # Everything between the second index and excluding the last element
    myArray[1:-1]
    myList[:-5]
```

## _Parameters vs Arguments_
- Parameters are the variables inside of a function that are used for reference
- Arguments are the variables passed to a function when calling the function
    ```
    # Here "num" is the parameter
    def printMyNumber(num):
        print(num)

    def callingFunction():
        # Here 4 is the argument
        printMyNumber(4)
    
*__Default Arguments__*

Default arguments are used for functions where you want a default value (WOW!) for a parameter

    def printMyNumber(num=80):
        print(num)

    def callingFunction():
        # Prints 4 like we expect
        printMyNumber(4)
        # Prints 80 since we didn't give it a value
        printMyNumber()

## _Static vs Instance Variables_
Those familiar with other popular languages like C++ and Java are likely familiar with the concepts of static and instance class variables. For those that aren't, instance variables are like the attributes per class discussed above where each Ball has its own color. Instance variables are owned by each individual instance of the class.

Static variables are a bit different in that they are owned by all members of a particular class. You can interact with them similarly to instance variables, but the scope is different. This comes in handy when you may want to keep a running total of how many Balls have been created. It wouldn't make much sense for each Ball class to have its own copy of the total amount of balls, would it? The effect can be shown below in python.
```
# Static variable 'ballCount' belonging to the class Ball is currently 0
myNewBall.ballCount = 0
# The += is a concatenation operator where it equals itself plus the expression
myNewBall.ballCount += 1
anotherBall.ballCount += 1
print(myNewBall.ballCount)
# 2
```
- Why is the print showing 2 when myNewBall's ball count is supposed to be 1? It is because ballCount is a static variable that anotherBall is able to update it and access it. It is a shared attribute.

*__Why is this interesting in python?__*

Well, it caused me some grief since usually other languages will use a `static` keyword in front of the class variable rather than being dependent upon placement.
```
class Ball:
    # This is the static variable ballCount intializing to 0
    ballCount = 0

    # The __init__ function is what is called as the constructor when Ball() is used
    def __init__(self, ballColor="", ballWeight=""):
        # color and weight are attributes that are instance variables
        self.color = ballColor
        self.weight = ballWeight
```
_Note: For python class functions, self must be a parameter so that you can explicitly access attributes and methods for a given class instance_

## _Switch Statements in Python_
*__What are switch statements?__*

Inevitably once you start programming, you will encounter a situation like below:
    
    if (inpString == "Up"):
        stuff()
    elif (inpString == "Down"):
        andStuff()
    elif (inpString == "Right"):
        andMoreStuff()
    elif (inpString == "Left"):
        otherStuff()
    elif (inpString == "Forward") or (inpString == "Backward"):
        oneActionForTwoCases()
    else:
        somethingWentWrong()
    
To counteract this repetitive and annoying typing and viewing experience, switch statements with cases are used.
```
    switch(inpString) {
        case "Up":
            stuff();
            break;
        case "Down":
            andStuff();
            break;
        case "Right":
            andMoreStuff();
            break;
        case "Left":
            otherStuff;
            break;
        case "Forward":
        case "Backward":
            oneActionForTwoCases();
            break;
        default:
            somethingWentWrong();
    }
```
The case statement used above is in C++ syntax. Switch statements are nice for filtering a variable's potential values and mapping them to actions while having a catch-all default case. You might notice that the "Forward" and "Backward" cases are smushed together. This is intentional since some languages support "fall through statements". It is exactly what it sounds like since you can fall through into another case if you don't include that language's "break" statement inside the case.


*__Python's Take on Switch Statements__*

Having explained what switch statements are, switch statements are fantastic in Python! Well, that would probably be true if they actually had them. You can utilize similar functionality, but it is in a bit of a different fashion and syntax than the switch statement shown above. A way (that was used in this program) to represent switch functionality is by utilizing a python dictionary.

*__Python Dictionaries__*

A Python dictionary is a structure similar to a list and array that instead has a defining characteristic of key-value pairs. A dictionary is not restricted to integer indexing and instead becomes a set of values mapping to other values. THe way to distinguish keys and values is that the keys act as the index (what you put between the square brackets) that will allow the dictionary to return a value.
```
    def myFunc():
        print("Hello!)

    myDict = {}

    # The key is "apple" and the value is "red"
    myDict["apple"] = "red"
    print(myDict["apple"]) # red

    myDict[4] = "four"
    print(myDict[4]) # four

    myDict["func"] = myFunc
    myDict["func"]() # Hello!
```
That all makes sense with the examples, right? Wait a second. I just assigned a function as a value for myDict. That doesn't really seem right, does it? Well, it depends on who you ask. As a part of OOP, the discussion of things called "first class citizens" and what all they include will vary from language to language.

A "first class citizen" essentially means that it is a particular part of a programming language is for all intents and purposes basically acts like an int, string, or other similar primitive types. This is a topic that can get complicated, but this is essentially the idea. C++ by contrast will generally handle functions as pointers and references to other pieces of code rather than viewing them as objects like Python. This is because the two languages have very different dogmas and purposes.

*__Using a Dictionary as a Switch Statement__*

Since you can use functions as values in a dictionary, you create a jump table. A jump table is in essence what a switch statement is while having a few other features like default cases. A jump table is basically a way to have a value map directly to an action in an instant access fashion. This is very similar to how arrays in most programming langauges have instant access to a value. To show how this idea vares, you can accomplish a jump table in C++ similar to a Python dictionary by assigning function pointers to array slots or by using normal old switch statements.

This jump table functionality with dictionaries is used by mapping a retailer to a an html downloading and processing function specific to that retailer website.
```
  # URL_PROCESSOR_MAPPER is the dictionary, the retailer is the key,
  # the value is the specific function assigned elsewhere with the retailer key,
  # link is a common argument passed to the function that is held as the value,
  # and the function will return its results to resultList
  resultList = URL_PROCESSOR_MAPPER[retailer](link)
```
## _Use of Tuples_

A tuple is an ordered immutable set that stores values similarly to a list. A list doesn't have to be ordered and is mutable (can be directly changed). They have different uses for different applications, but I wanted to highlight how they are used in this application since they are a good way to organize conditonals.
```
    if cmdFirstArg in ("", "h", "help"):
    # rather than
    if (cmdFirstArg == "") or (cmdFirstArg == "h") or (cmdFirstArg == "help"):
```

## _Python Regexes_

Regexes are "**reg**ular **ex**pressions" that are essentially just templates used for pattern matching. There are different formats for different regex standards, but they are generally fairly similar with the symbols and patterns that are used. An example would be that `\d+.\d+` will match either `123542.3` or `0.43223` but not `.34242` or `2.` due to the `+` symbol. The `+` symbol stands for matching the previous element (`\d` which is any number) one or more times which is not achieved in both of the last two examples.

Regexes are better understood once you use them quite a bit, so I reccommend that you look at Python's [regex documentation](https://developers.google.com/edu/python/regular-expressions), Microsoft's [reference guide](https://docs.microsoft.com/en-us/dotnet/standard/base-types/regular-expression-language-quick-reference), and other tutorials to get the full grasp of the utility of regular expressions.

Regexes are used rather extensively in this program, so a few notes to highlight are:
- The `r` before a string like in `r'\bhttps.*\b'` tells Python that the string should be interpreted as a raw string without any processing. Python will otherwise attemp to interpret all the backslash `\` pairs like `\b`, `\n`, and `\t` in the context of ASCII, Unicode, or other character standards.
- Be extremely mindful of lazy vs greedy regex expressions. The difference is that lazy will stop the first time the pattern is matched whereas greedy may attempt to match until the very last character.
  ```
    # Let's say you want to use a regex to get the first angle bracket (<>) sequence
    str = "<Hello> <Hullo> (Hi)"

    # A reasonable regex may be `<.*>`
    foundStr = re.find(r"<.*>", str).group()
    print(foundStr) # <Hello> <Hullo>

    # That's not what we wanted. Why? The sequence is greedy by default.
    # To make it not greedy, thus lazy, you must use ? with the wildcard operator *
    foundStr = re.find(r"<.*?>", str).group()
    print(foundStr) # <Hello>
  ```