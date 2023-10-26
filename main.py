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

@app.route("/spotifyauth")
def spotifyauth():
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



    return gettopartists(token_info["access_token"])

def gettopartists(token):
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(API_BASE_URL + "me/top/artists", headers=headers)

    playlists = response.json()

    return jsonify(playlists)
