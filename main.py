import urllib.parse

import flask
import requests

from flask import Flask, redirect, request, jsonify
from flask import render_template

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

REDIRECT_URL = "http://127.0.0.1:5000/getspotifydata"
CLIENT_ID = "f0ec4ee27a08406b99511ea8d7997743"
CLIENT_SECRET = "3e24194e95d14d39a08ea1841d4e31a8"

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/spotifyauth", methods=["POST"])
def spotifyauth():
    global type_of_request
    type_of_request = request.form.get("type")

    scope = "user-read-private user-read-email user-top-read"

    params = {"client_id": CLIENT_ID, "response_type": "code", "scope": scope, "redirect_uri": REDIRECT_URL, "show_dialog": True}

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)} "

    return redirect(auth_url)

@app.route("/getspotifydata")
def getspotifydata():
    if "error" in request.args:
        return jsonify({"error": request.args["error"]})

    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URL,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

    artists = gettopartists(token_info["access_token"])

    tracks = gettoptracks(token_info["access_token"])

    artisthtml = "<div style='float: left; width: 300px;'>Artist<ol>"
    for a in artists:
        artisthtml += "<li>" + a["name"] + "</li>"

    artisthtml += "</ol></div>"

    trackhtml = "<div style='float: left; width: 600px;'>Track<ol>"
    for a in tracks:
        trackhtml += "<li>" + a["name"] + " by " + a["artists"][0]["name"] + "</li>"

    artisthtml += "</ol></div>"


    return artisthtml + trackhtml

def gettopartists(token):
    headers = {"Authorization": f"Bearer {token}"}
    partial_url = ""

    if type_of_request == "shortterm":
        partial_url = "me/top/artists?time_range=short_term&limit=50"
    elif type_of_request == "mediumterm":
        partial_url = "me/top/artists?time_range=medium_term&limit=50"
    else:
        partial_url = "me/top/artists?time_range=long_term&limit=50"

    response = requests.get(API_BASE_URL + partial_url, headers=headers)

    topArtists = response.json()

    artists = topArtists["items"]

    artists.sort(key=sortpopularity, reverse=True)

    return artists

def gettoptracks(token):
    headers = {"Authorization": f"Bearer {token}"}
    partial_url = ""

    if type_of_request == "shortterm":
        partial_url = "me/top/tracks?time_range=short_term&limit=50"
    elif type_of_request == "mediumterm":
        partial_url = "me/top/tracks?time_range=medium_term&limit=50"
    else:
        partial_url = "me/top/tracks?time_range=long_term&limit=50"

    response = requests.get(API_BASE_URL + partial_url, headers=headers)

    topTracks = response.json()

    tracks = topTracks["items"]

    tracks.sort(key=sortpopularity, reverse=True)

    return tracks


def sortpopularity(e):
  return e['popularity']


