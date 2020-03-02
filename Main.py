import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd

# User's Collection
myCollection = []

# Creating the CSV file to save the User's Collection
if os.path.isfile("./myCollection.csv") == True:
    with open("myCollection.csv", "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            myCollection.append(row)
else:
    with open("myCollection.csv", "w") as csv_file:
        fieldnames = ["Title", "Condition", "Price", "Platform"]
        gamewriter = csv.DictWriter(csv_file, fieldnames=fieldnames)
        gamewriter.writeheader()


# Div id's and their corresponding names
priceTypesId = ["price-loose", "price-cib", "price-new"]
priceTypes = ["Loose:", "CIB:", "New:"]

startingOptions = ["Add a game", "Delete a game", "Show my collection", "Save and quit"]

def gameCollected():
    isCollected = input("What condition do you have the game in? ")
    if isCollected == "Loose" or isCollected == "loose":
        print("\nGame added with \"Loose\" condition")
        myCollection.append({"Title": gameTitle, "Condition": "Loose",
                             "Price": prices.findChild("div", {"id": "price-loose"}).findChild("h3").text.strip(),
                             "Platform": gamePlatform})
    elif isCollected == "Cib" or isCollected == "CIB" or isCollected == "cib":
        print("\nGame added with \"Complete\" condition")
        myCollection.append({"Title": gameTitle, "Condition": "CIB",
                             "Price": prices.findChild("div", {"id": "price-cib"}).findChild("h3").text.strip(),
                             "Platform": gamePlatform})
    elif isCollected == "New" or isCollected == "new":
        print("\nGame added with \"New\" condition")
        myCollection.append({"Title": gameTitle, "Condition": "New",
                             "Price": prices.findChild("div", {"id": "price-new"}).findChild("h3").text.strip(),
                             "Platform": gamePlatform})
    else:
        print("\nInvalid Condition: Try Again")
        gameCollected()

programRunning = True

while programRunning:
    # Starting Options
    choiceNum = 1
    for option in startingOptions:
        print(str(choiceNum) + ")", option)
        choiceNum += 1

    optionChoice = input("\nWhat would you like to do? ")

    if optionChoice == "1":

        addGameRunning = True
        while addGameRunning:
            # Initial Web Request
            search = input("\nEnter Game Title: ").replace(" ", "+").lower()
            website = "https://gamevaluenow.com"
            r = requests.get(website + "/search?platform=0&search=" + search)
            soup = BeautifulSoup(r.text, "html.parser")
            results = soup.find("div", {"class": "result-list"})

            # Search Results
            games = results.findAll("div", {"class": "result-title"})
            gamesList = []

            # Choose Game From Search Results
            i = 1
            for game in games:
                if game.text.strip() == "Title":
                    continue
                gamesList.append(game)
                print(str(i) + ")", game.text.strip(), "Platform:", game.findNext("div", {"class": "result-platform"}).text.strip())
                i += 1

            chosenGame = input("\nType the game's number: ")

            # Setting the request to be the games page
            chosenGame = gamesList[int(chosenGame) - 1]
            gamePage = chosenGame.findParent(href=True).attrs['href']
            gr = requests.get(website + gamePage)
            soup = BeautifulSoup(gr.text, "html.parser")

            # Print Game Title
            gameTitle = soup.find("div", {"id": "price-chart-container"}).findChild("h1").text.strip()
            gamePlatform = gamePage.split("/")[1].replace("-", " ").capitalize()
            print(gamePlatform)
            print("\n" + gameTitle)

            # Scraping for the game's prices
            prices = soup.find("div", {"id": "market-values"})
            x = 0
            for type in priceTypesId:
                value = prices.findChild("div", {"id": priceTypesId[x]})
                if value != None:
                    print(priceTypes[x], value.findChild("h3").text.strip())
                else:
                    print(priceTypes[x], "N/A")
                x += 1

            gameCollected()

            with open("myCollection.csv", "w") as csv_file:
                fieldnames = ["Title", "Condition", "Price", "Platform"]
                gamewriter = csv.DictWriter(csv_file, fieldnames=fieldnames)

                gamewriter.writeheader()
                for game in myCollection:
                    gamewriter.writerow(game)

            restartSearch = input("\nWould you like to add another game?")
            if restartSearch == "y" or restartSearch == "yes" or restartSearch == "Y" or restartSearch == "Yes":
                continue
            elif restartSearch == "n" or restartSearch == "no" or restartSearch == "N" or restartSearch == "No":
                addGameRunning = False

    if optionChoice == "2":
        i = 1
        for game in myCollection:
            print(str(i) + ")", game["Title"])
            i += 1

        deleteChoice = input("Which game would you like to delete? ")
        if deleteChoice != "0":
            myCollection.pop(int(deleteChoice)-1)

    if optionChoice == "3":
        print("\n")
        collectionTable = pd.read_csv("myCollection.csv", index_col="Title").sort_values(["Platform", "Title"])
        collectionValue = 0
        for game in myCollection:
            collectionValue = collectionValue + float(game["Price"].replace("$", ""))

        print(collectionTable, "\n\nTotal Value: $" + str(collectionValue), "\n")

    if optionChoice == "4":
        print("Saving...")

        # Adding games to the CSV file
        with open("myCollection.csv", "w") as csv_file:
            fieldnames = ["Title", "Condition", "Price", "Platform"]
            gamewriter = csv.DictWriter(csv_file, fieldnames=fieldnames)

            gamewriter.writeheader()
            for game in myCollection:
                gamewriter.writerow(game)

        print("Saved.\n")
        programRunning = False
