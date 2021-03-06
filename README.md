# Roomba Puzzle

I've been running into some problems recently; I bought a Roomba a few months ago, and although I know the exact dimensions of my room, and the locations of dirt at any one moment (I track it religiously), I simply can't figure out how many patches of dirt would have been swept up if I give it a certain set of directions! I'd also like to persist my Roomba's journeys to a DB, so that I can go back and remember the good times.

Sounds like a bit like a programming exercise, doesn't it? 
https://gist.github.com/alirussell/9a519e07128b7eafcb50

### The Solution

This problem boils down to a move-and-record - we want to extract relevant information from a JSON payload, walk through the instruction set, updating our location recording any coordinates we visited that contained dirt.

I've implemented this as a Flask app in Python 3.7 + Redis, which is tested using PyTest, and Dockerised. There were a few interesting points in this exercise:

* We need to clean the starting position, as the Roomba is always on.
* The return values should be the number of patches cleaned, *not* the number remaining.
* When we exceed the room dimensions, we don't move, we hit the wall for as many directions as we don't progress.
* If we're persisting to a DB, and this is a functional problem, we can cache responses instead of re-executing. We need to index on a composite key of all inputs.
* This problem would lend itself to recursion pretty well

### Getting Started

To run the Docker image, simply run the following command:

```
docker-compose up -d
```

This spins up our app server running on Flask, and a Redis server - exposing the REST API on port 80. You can perform requests in a REST client or programatically using the routes below.

To run the test suite once the service is up, in the root directory:

```
pytest
```

### Routes

#### POST /
##### Headers
*Content-Type*: application/json

##### Body
`{"roomSize" : [5, 5], "coords" : [1, 2], "patches" : [[1, 0], [2, 2], [2, 3]], "instructions" : "NNESEESWNWW"}`

* *roomSize* : A two-element list of the integeric size of the room in the format [x,y]. Defines the maximum bounds for our Roomba.
* *coords* : A two-element list of the starting position of the Roomba, in the format [x,y].
* *patches* : A list of lists, two-elements each, integeric. These are the coordinates where we know there to be dirt. Each time the Roomba passes over one of these, we count it as cleaned.
* *instructions* : a stringified list of North, East, South, and West instructions, determining where the Roomba will travel.

##### Response

200 - Successful
`{"coords" : [1, 3], "patches" : 1}`

* *coords* : The ending position of the Roomba
* *patches* : The number of patches we were able to clean in this run

---

400 - Bad Request

The JSON POSTed was in an incorrect format, we couldn't proceed.

### Expansion

Following on, there's a few ways I would expand this project with more time, or if productionising in some way:

* We're only logging to `STDOUT` if the `FLASK_ENV` is 'dev'; we probably want to add some proper logging infrastructure.
* Ideally, we might like a frontend to display Roomba progress - I'd tackle this in Javascript with a roomSize grid of divs, AJAX calls to Flask and an update of background-color. As the task sort of demands that the algo executes in a single step, I didn't want to rewrite it in JS which is probably what I'd do as it's not a complex task, and there are no server-side components. (JS is not an accepted solution language)
* For the sake of keeping things easy, I've indexed on a SHA256 of the inputs, if we were concerned about bigger rooms and larger instruction sets, we could try and calculate whether a certain set of instructions has been executed in a room that had smaller dimensions and didn't hit the walls, meaning we could return a cached response even though the roomSize is different.
* Simarlarly, we could optimise by not even running the algo if there are no instructions, and not keeping track of patches if none were provided.
* If # of Roombas > 1, that would get interesting. Each device would run in parallel and sync patches of dirt that had been cleaned, as well as checking whether the next position already has a device in it, or if it's about to. 
* Roombas have to return to base to charge up (I believe) - it'd be interesting to keep track of battery level and have to navigate back to 0,0 if it got too low, cleaning on the way. 
