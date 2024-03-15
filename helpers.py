import requests


def lookup(movie):
    """ Lookup a movie """

    # My API key
    api_key = "<api key goes here>"

    # Construct the API request URL
    url = f"http://www.omdbapi.com/?apikey={api_key}&s={movie}"

    # Make the request and handle the response
    response = requests.get(url)
    data = response.json()

    return(data)

def lookup_imdbid(id):
    """ Lookup a movie via its IMDB ID """

    # My API key
    api_key = "7d4ed119"

    imdb_id = id

    # Construct the API request URL
    url = f"http://www.omdbapi.com/?apikey={api_key}&i={imdb_id}"

    # Make the request and handle the response
    response = requests.get(url)
    data = response.json()

    return(data)






