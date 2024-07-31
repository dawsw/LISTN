from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
import os
import math
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from requests import post, get
from helpers import search_albums, get_new_releases, get_top_songs, login_required, Album, sp, fetch_album_info, playlist_list, fetch_track_info
import concurrent.futures
from functools import partial


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# assign database
db = SQL("sqlite:///database.db")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        #register
        if 'confirm_password' in request.form:

            # clear any user_ids
            session.clear()

            # check to see if username already taken
            rows = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username")))

            if rows:
                message = "Username already taken. Try another"
                return render_template("layout.html", message=message)
        
            # if password/confirm password dont match
            if request.form.get("password") != request.form.get("confirm_password"):
                message = "Passwords do not match."
                return render_template("layout.html", message=message)
            
            special_chars_pattern = re.compile(r'[!@#$%^&*()_+=\[{\]};:<>|./?,-]')
            if special_chars_pattern.search(request.form.get("username")):
                message = "Username must only contain letters or numbers."
                return render_template("layout.html", message=message)
            
            # get username/password and hash password
            username = request.form.get('username')
            hash = generate_password_hash(request.form.get("password"))

            # insert into
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

            user_rows = db.execute("SELECT id FROM users WHERE username = ?", username)
            session["user_id"] = user_rows[0]["id"]

            return redirect('/home')
        
        #login
        else: 

            # clear any user_ids
            session.clear()

             # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                message = "Invalid Username or Password"
                return render_template("layout.html", message=message)

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/home")
    
    elif request.method == 'GET':
        return render_template("index.html")
    


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == 'POST':
        return render_template("home.html")
    elif request.method == 'GET':
        playlists = playlist_list
        top_songs = get_top_songs(sp)
        new_albums = get_new_releases(sp)
        return render_template("home.html", top_songs=top_songs, new_albums=new_albums, playlists=playlists)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == 'POST':
        return redirect(url_for('home'))
    elif request.method == 'GET':
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]
        album_ids = db.execute("SELECT album_id FROM user_albums WHERE user_id = ? ORDER BY timestamp DESC", session["user_id"])
        wishlist_ids = db.execute("SELECT album_id FROM user_wishlists WHERE user_id = ? ORDER BY timestamp DESC", session["user_id"])

        #get list of wishlist albums
        wishlist_albums = []
        wishlist_total_albums = 0
        for id in wishlist_ids:
            wishlist_total_albums += 1
            album = Album(id["album_id"], sp)
            wishlist_albums.append(album)

        # get list of LISTN albums
        albums = []
        total_albums = 0
        for id in album_ids:
            total_albums += 1
            album = Album(id["album_id"], sp)
            albums.append(album)

        return render_template("profile.html", albums=albums, username=username["username"], total_albums=total_albums, wishlist_total_albums=wishlist_total_albums, wishlist_albums=wishlist_albums)
    

@app.route("/profile_user", methods=["GET", "POST"])
@login_required
def profile_user():
    if request.method == 'POST':
        return redirect(url_for('home'))
    elif request.method == 'GET':
        current_username = db.execute("SELECT username FROM users WHERE id = ?", session['user_id'])[0]['username']
        profile_username = request.args.get('username')
        user_id = db.execute("SELECT id FROM users WHERE username = ?", profile_username)
        album_ids = db.execute("SELECT album_id FROM user_albums WHERE user_id = ?", user_id[0]['id'])
        wishlist_ids = db.execute("SELECT album_id FROM user_wishlists WHERE user_id = ? ORDER BY timestamp DESC", user_id[0]['id'])

        #get list of wishlist albums
        wishlist_albums = []
        wishlist_total_albums = 0
        for id in wishlist_ids:
            wishlist_total_albums += 1
            album = Album(id["album_id"], sp)
            wishlist_albums.append(album)

        # get list of LISTN albums
        albums = []
        total_albums = 0
        for id in album_ids:
            total_albums += 1
            album = Album(id["album_id"], sp)
            albums.append(album)

        return render_template("profile.html", albums=albums, profile_username=profile_username, current_username=current_username, total_albums=total_albums, wishlist_total_albums=wishlist_total_albums, wishlist_albums=wishlist_albums)


@app.route("/playlists", methods=["GET", "POST"])
@login_required
def playlists():
    if request.method == 'POST':
        return redirect(url_for('home'))
    elif request.method == 'GET':
        playlist_id = request.args.get('playlist')
        playlist_name = request.args.get('name')
        results = sp.playlist_tracks(playlist_id)
        track_ids = [track['track']['id'] for track in results['items'][:18]]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Fetch album details concurrently
            fetch_album_partial = partial(fetch_track_info, sp=sp)
            tracks = list(executor.map(fetch_album_partial, track_ids))

        return render_template("playlist.html", tracks=tracks, playlist_name=playlist_name)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == 'POST':
        searched_album = request.form.get('search')

        if not searched_album.strip():
            return redirect('home.html')
        
        albums = search_albums(searched_album, sp)
        usernames = []
        
        #check to see if search results in any usernames
        found_usernames = db.execute('SELECT username FROM users WHERE username LIKE ?', ('%' + searched_album + '%'))
        if found_usernames:
            for name in found_usernames:
                usernames.append(name['username'])
        
        return render_template("search.html", albums=albums, searched_album=searched_album, usernames=usernames)
    
    elif request.method == 'GET':
        return render_template("home.html")


@app.route("/album_details", methods=["GET", "POST"])
@login_required
def album_details():
    global album_id 
    if request.method == 'POST':
        # see if user is trying to delete rating
        if 'deletebutton' in request.form:
            db.execute("DELETE FROM user_albums WHERE user_id = ? AND album_id = ?", session["user_id"], album_id)
            return redirect(url_for('profile'))
        
        if 'wishlistbutton' in request.form:
            db.execute("INSERT INTO user_wishlists (user_id, album_id) VALUES (?, ?)", session["user_id"], album_id)
            return redirect(url_for('profile'))
        
        if 'del_wishlistbutton' in request.form:
            db.execute("DELETE FROM user_wishlists WHERE user_id = ? AND album_id = ?", session["user_id"], album_id)
            return redirect(url_for('profile'))
        0
        # get comments and score
        comments = request.form.get('comments')
        if not comments:
            comments = 'No comments.'
        
        score = request.form.get('score')

        # get all existing album ids from user and see if they already rated that album
        album_ids = db.execute("SELECT album_id FROM user_albums WHERE user_id = ?", session["user_id"])
        
        for id in album_ids:
            if id["album_id"] == album_id:
                db.execute("UPDATE user_albums SET rating = ?, comments = ? WHERE user_id = ? AND album_id = ?", score, comments, session["user_id"], album_id)
                return redirect(url_for('profile'))
            
        # otherwise add new rating into database
        db.execute("INSERT INTO user_albums (user_id, album_id, rating, comments) VALUES (?, ?, ?, ?)", session["user_id"], album_id, score, comments)
        
        # see if user has album in their wishlist & remove it if so.
        album_in_wishlist = db.execute("SELECT album_id FROM user_wishlists WHERE user_id = ? AND album_id = ?", session["user_id"], album_id)
        if album_in_wishlist:
            db.execute("DELETE FROM user_wishlists WHERE user_id = ? AND album_id = ?", session["user_id"], album_id)
        
        #return to profile page
        return redirect(url_for('profile'))
     
    elif request.method == 'GET':
        referrer = request.referrer
        active_username = db.execute("SELECT username from users where id = ?", session['user_id'])[0]['username']
        #if coming from search page/ own profile
        if 'username' not in referrer:
            album_id = request.args.get('album_id')
            album = Album(album_id, sp)

            all_ratings = db.execute("SELECT user_albums.user_id, user_albums.rating, user_albums.timestamp, users.username FROM user_albums JOIN users ON user_albums.user_id = users.id WHERE user_albums.album_id = ? ORDER BY user_albums.timestamp DESC", album_id)
            
            #see if user has album in their wishlist
            wishlist_id = db.execute("SELECT album_id FROM user_wishlists WHERE user_id = ? AND album_id = ?", session["user_id"], album_id)
            in_wishlist = 'No'

            if wishlist_id:
                in_wishlist = 'Yes'

            # if other people have rated this album
            if all_ratings:
                ratings_list = []
                total_ratings = 0
                listn_score = 0
                for row in all_ratings:
                    # Convert the timestamp string to a datetime object
                    row['timestamp'] = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')

                # append each score from all_ratings to ratings_list
                for row in all_ratings:
                    score = row['rating']
                    total_ratings += 1
                    ratings_list.append(score)

                # add each item in ratings_list to listn_score
                for score in ratings_list:
                    listn_score += score

                # divide listn_score by number of total_ratings
                listn_score = math.ceil(listn_score / total_ratings)

                # see if user has rated this album
                try:
                    score = db.execute("SELECT rating FROM user_albums WHERE user_id = ? AND album_id = ?", session["user_id"], album_id)[0]['rating']
                    comments = db.execute("SELECT comments FROM user_albums WHERE user_id = ? AND album_id = ?", session["user_id"], album_id)[0]['comments']
                
                except (IndexError, UnboundLocalError):
                    return render_template("album_details.html", album=album, listn_score=listn_score, total_ratings=total_ratings, all_ratings=all_ratings, in_wishlist=in_wishlist, active_username=active_username)

            # if no one has rated the album
            else:
                total_ratings = 0
                return render_template("album_details.html", album=album, total_ratings=total_ratings, in_wishlist=in_wishlist)
        
            # return all information if the user has rated the album
            return render_template("album_details.html", album=album, score=score, comments=comments, listn_score=listn_score, total_ratings=total_ratings, all_ratings=all_ratings, in_wishlist=in_wishlist, active_username=active_username)
        
        #if coming from other person's profile
        elif 'username' in referrer:
            # get username from previous website url
            parsed_url = urlparse(referrer)
            query_params = parse_qs(parsed_url.query)
            username = query_params.get('username', [''])[0]

            # get the active users username
            current_username = db.execute("SELECT username FROM users WHERE id = ? ", session['user_id'])[0]['username']

            # get album id from current url
            album_id = request.args.get('album_id')
            
            # get user id based off username
            user_id = db.execute("SELECT id FROM users WHERE username = ? ", username)[0]['id']

            all_ratings = db.execute("SELECT user_albums.user_id, user_albums.rating, user_albums.timestamp, users.username FROM user_albums JOIN users ON user_albums.user_id = users.id WHERE user_albums.album_id = ? ORDER BY user_albums.timestamp DESC", album_id)

            # if other people have rated this album
            if all_ratings:
                ratings_list = []
                total_ratings = 0
                listn_score = 0
                for row in all_ratings:
                    # Convert the timestamp string to a datetime object
                    row['timestamp'] = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')

                # append each score from all_ratings to ratings_list
                for row in all_ratings:
                    score = row['rating']
                    total_ratings += 1
                    ratings_list.append(score)

                # add each item in ratings_list to listn_score
                for score in ratings_list:
                    listn_score += score

                # divide listn_score by number of total_ratings
                listn_score = math.ceil(listn_score / total_ratings)

                album = Album(album_id, sp)

                # see if user has rated this album
                try:
                    score = db.execute("SELECT rating FROM user_albums WHERE user_id = ? AND album_id = ?", user_id, album_id)[0]['rating']
                    comments = db.execute("SELECT comments FROM user_albums WHERE user_id = ? AND album_id = ?", user_id, album_id)[0]['comments']
                except (IndexError, UnboundLocalError):
                    return render_template("album_details.html", album=album, listn_score=listn_score, total_ratings=total_ratings, all_ratings=all_ratings)

            # if no one has rated the album
            else:
                total_ratings = 0
                return render_template("album_details.html", album=album, total_ratings=total_ratings)
        
            # return all information if the user has rated the album
            return render_template("album_details.html", album=album, score=score, comments=comments, listn_score=listn_score, total_ratings=total_ratings, all_ratings=all_ratings, username=username, current_username=current_username)
    
if __name__ == "__main__":
    app.run(debug=True)

















































































