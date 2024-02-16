from fastapi import FastAPI, Response
from typing import Optional, Union
from copy import deepcopy
import json
import random
import re
from pydantic import BaseModel
import base64

app = FastAPI()

class Reading(BaseModel):
    id: Optional[int] = None
    readingType: str
    description: str
    card_list: Optional[list] = None
    sum:Optional[int] = None

# Sample history
with open ('./app/history.json') as f:
    data = json.load(f)
    history = data["history"]
    # Get the last id from the history
    reading_count = history[-1]["id"]

@app.get("/")
def read_root():
    return "Let's get divining \N{crystal ball}"

# Get the list of all cards
@app.get("/cards")
def get_cards():
    with open ('./app/tarot.json') as f:
        data = json.load(f)
    return data["cards"]

# Acceptable cardTypes: major, minor, cups, swords, wands, pentacles
@app.get("/cards/{cardType}")
def get_cards_ref_cardType(response: Response, cardType: str):
    with open ('./app/tarot.json') as f:
        data = json.load(f)

    match cardType:
        case "major":
            return [card for card in data["cards"] if card["arcana"] == "Major Arcana"]
        case "minor":
            return [card for card in data["cards"] if card["arcana"] == "Minor Arcana"]
        case "cups":
            return [card for card in data["cards"] if card["suit"] == "Cups"]
        case "swords":
            return [card for card in data["cards"] if card["suit"] == "Swords"]
        case "wands":
            return [card for card in data["cards"] if card["suit"] == "Wands"]
        case "pentacles":
            return [card for card in data["cards"] if card["suit"] == "Pentacles"]
        case _:
            response.status_code = 400
            return "Invalid card type."

# Do a tarot reading: love/career/anything really
@app.post("/reading")
def reading(reading: Reading, response:Response):
    global reading_count
    reading_count += 1
    # id and card list supposed to be assigned by the server, so we don't want to accept them from the client
    if reading.id is not None or reading.card_list is not None:
        response.status_code = 400
        return "Invalid POST request format. id and card_list should not be included in the request."
    # check for suspicious input
    max_length = 1000

    if len(reading.description) > max_length or len(reading.readingType) > max_length:
        response.status_code = 400
        return f"Input is too long. Maximum length is {max_length} characters."
    
    suspicious_patterns = [
        r"<script.*?>.*?</script>",  # Basic attempt to catch simple <script> injections
        r"exec\(.*?\)",  # Catches Python exec() usage
        r"eval\(.*?\)",  # Catches Python eval() usage
        r"system\(.*?\)",  # Catches system command injections
        r"[;]+",  # Checks for semicolons which might be used maliciously
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, reading.description, re.IGNORECASE) or re.search(pattern, reading.readingType, re.IGNORECASE):
            response.status_code = 400
            return f"Suspicious pattern detected: {pattern}"
            
    # Start divining
    with open ('./app/tarot-images.json') as f:
        data = json.load(f)
    # Select 3 random cards
    selected_cards = random.sample(data["cards"], 3)
    reading.card_list = selected_cards
    reading.id = reading_count
    sum = 0
    for card in selected_cards:
        sum += int(card["number"])
    reading.sum = sum
    history.append(dict(reading))
    # Return the reading as image binaries
    card_images = []
    card_image_files = [card["img"] for card in selected_cards]
    for i in range(len(card_image_files)):
        with open(f'./app/cards/{card_image_files[i]}', "rb") as f:
            card_images.append(base64.b64encode(f.read()))
    return card_images

# Get the history of readings
@app.get("/history")
def get_history(response: Response, limit: Optional[int] = None, sortBy: Optional[str] = None):
    # Sort by total number in reading (has no effect on the reading, just for checkoff purposes)
    # Make a copy of history so we don't modify the original
    sorted_history = deepcopy(history)
    if sortBy is not None:
        if sortBy.lower() == "number":
            sorted_history = sorted(history, key=lambda k: k['sum'])
        else:
            response.status_code = 400
            return "Invalid sortBy parameter."
    if limit is not None:
        if limit > 0:
            sorted_history = sorted_history[:limit]
        else:
            response.status_code = 400
            return "Invalid limit parameter. Limit should be a positive integer."
    return sorted_history

# Get a specific reading by readingType
@app.get("/history/{readingType}")
def get_reading(readingType: str, response: Response):
    result = [reading for reading in history if reading["readingType"] == readingType]
    if len(result) == 0:
        response.status_code = 404
        return "Reading not found."
    return result

# Delete a specific reading by id
@app.delete("/history/{param}")
def delete_reading(param: str, response: Response):
    global history
    # single delete using id
    if param.isnumeric():
        result = [reading for reading in history if reading["id"] == int(param)]
        if len(result) == 0:
            response.status_code = 404
            return "ID not found."
        history = [reading for reading in history if reading["id"]!= int(param)]
    #batch delete using readingType
    else:
        result = [reading for reading in history if reading["readingType"] == param]
        if len(result) == 0:
            response.status_code = 404
            return "Readings not found."
        history = [reading for reading in history if reading["readingType"]!= param]
    
    return result