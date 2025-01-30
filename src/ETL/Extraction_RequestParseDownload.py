# Sends and receives HTTP requests.
import requests

# Parses HTML documents into readable text.
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import os


def requestParseDownload():

    website = "https://whoicf2.whoi.edu/science/B/whalesounds/bestOf.cfm?code=BD15F" # + userInput
    htmlDoc = requests.get(website)
    # Response codes OTHER THAN 200-299 means something went wrong
    # print(htmlDoc)

    soup = BeautifulSoup(htmlDoc.content, "html.parser")

    # Find codes (str) for all selectable options of Watkins Marine Mammal common names
    form = soup.find("form", {"name": "jump1"})
    options = form.find_all('option')
    codes = []
    for option in options:
        match = re.search(r'code=([A-Z0-9]+)', option['value'])
        if match:
            codes.append(match.group(1))

    for code in codes:
        website = "https://whoicf2.whoi.edu/science/B/whalesounds/bestOf.cfm?code=" + code
        htmlDoc = requests.get(website)
        soup = BeautifulSoup(htmlDoc.content, "html.parser")

        div = soup.find("div", {"class": "database"})

        h3_tag = div.find("h3")
        if h3_tag:
            # Get the text from the tag
            text = h3_tag.text.strip()
            # Find the text after "of" and before "(<i>)"
            start = text.find("of") + len("of")
            end = text.find("(", start)
            mammalName = text[start:end].strip()
            print(mammalName)

        href = [a['href'] for a in soup.find_all('a', href=re.compile('/science.*.(mp3|wav|ogg|wma)'))]
        for h in href:
            filesToDownload = requests.get(f'https://whoicf2.whoi.edu{h}')
            # Extract file names from end of href calls, ex: 61025001.wav
            # Then open file for "write bytes" (wb)
            # Creates folders with mammal name if it does not exist
            fileName = "data/" + mammalName + "/" + urlparse(h).path.split("/")[-1]
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
            with open(fileName, 'wb') as f:
                f.write(filesToDownload.content)


if __name__ == "__main__":

    requestParseDownload()
