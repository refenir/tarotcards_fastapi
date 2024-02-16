# tarotcards_fastapi
For 50.012 Networks Lab 2
https://github.com/refenir/tarotcards_fastapi

## Set up
* Make sure to have docker installed
* Run `docker build -t python-tarotcardsfastapi .`
* Then, run `docker run -p 8000:80 python-tarotcardsfastapi`, and open http://127.0.0.1:8000/ to see "Let's get divining 🔮"

## Checkoff criteria
### GET requests (tarot cards and reading history)
* To get all the tarot cards, go to http://127.0.0.1:8000/cards
* To get all the cards in the major arcana, go to http://127.0.0.1:8000/cards/major
* To get all the sword cards in the minor arcana, go to http://127.0.0.1:8000/cards/swords
> [!NOTE]
> The valid inputs are `major`, `minor`, `swords`, `cups`, `wands`, `pentacles`.

* To get the complete history of the readings done, go to http://127.0.0.1:8000/history ; some sample will already be preloaded
* To get the complete history sorted by sum of the divined card numbers, go to http://127.0.0.1:8000/history?sortBy=number
* To get only 3 reading histories, go to http://127.0.0.1:8000/history?limit=3
* To get only 3 reading histories while sorted by the sum of divined card numbers, go to http://127.0.0.1:8000/history?limit=3&sortBy=number
* To get the history of a specific type of reading, go to http://127.0.0.1:8000/history/career
> [!NOTE]
> The type of reading will be specified during the POST request

### POST requests (tarot card reading)
To start a career reading, open up a terminal and type in `curl -H "Content-Type: application/json" -d '{"readingType":"career", "description":"what can I do to get my coworker fired?"}' -X POST http://127.0.0.1:8000/reading`
* This will return the base64 encoded binary file of 3 images of the divined cards
* By going back to http://127.0.0.1:8000/history, the new reading will be listed there as the highest id number

### DELETE requests (delete history)
* To delete the reading with id 2, open up a terminal and type in `curl -X DELETE http://127.0.0.1:8000/history/2`
* To batch delete all the embarrassing love readings, open up a terminal and type in `curl -X DELETE http://127.0.0.1:8000/history/love`

### Idempotent paths
The GET and DELETE paths are idempotent
* All the GET requests are purely reading the JSON files, without any modification to them. Thus, when multiple identical GET requests are received, they all give the same response
![alt text](/screenshots/GET_requests.png)
* The DELETE request is idempotent as multiple DELETE requests will not change the delete state. The first DELETE request will return a 200, while consecutive identical DELETE requests will return a 404. Thus, the request will be different after the first request, but there will be no change in state when multiple identical DELETE request comes in
![alt text](/screenshots/DELETE_requests.png)
![alt text](/screenshots/DELETE_requests_1.png)
