import tweepy
import os
import time
import sqlite3
import discord
import requests

#Twitter Authentication
consumer_key = ""
consumer_secret = ""
consumer_bearer_token = ""

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

#Discord Authentication
#Insert webhook link here
discord_link = ""
webhook = discord.Webhook.from_url(discord_link, adapter=discord.RequestsWebhookAdapter())


def main():
  user = input("Please enter the twitter handle.\n")

  if (user[0] == '@'):
      user = user[1 : len(user)]

  if (type(user) != str):
      raise TypeError

  #ID of user
  userID = get_user(user).id_str

  #Create database
  createDatabase(userID)

  #Create table if doesn't exist
  cursor.execute("CREATE TABLE IF NOT EXISTS followings(twID INTEGER)")
  #Check if table is empty, if so add all exisiting followers inside
  cursor.execute("SELECT count(*) FROM followings")
  if (cursor.fetchone()[0] == 0):
    firstRun(userID)
  # Execute 1 min loop
  while True:
    print("Checking followers now...")
    runMonitor(userID)
    print("Done.")
    time.sleep(62)

def handle_ratelimit(cursor):
  while True:
    try:
      yield next(cursor)
    except tweepy.RateLimitError:
      print("Rate limited. Sleeping for 15 mins")
      time.sleep(15*60)

def get_user(username):
  return api.get_user(username)

#obselete but just in case needed in future
def get_followingname(id, username):
  print(username + " is following: ")
  for follower in handle_ratelimit(tweepy.Cursor(api.friends_ids, user_id=id).items()):
    print(api.get_user(follower).screen_name)

def get_followingid(id):
  return api.friends_ids(user_id = id)

#Populate database for first run
def firstRun(twID):
  ids = get_followingid(twID)
  for id in ids:
    cursor.execute("SELECT EXISTS(SELECT twID FROM followings WHERE twID=?)", (id,))

    if (cursor.fetchone()[0] == 0):
      cursor.execute("INSERT INTO followings VALUES(?)", (id,))
    else:
      print("ID: " + str(id) + " already inside database.")

  db.commit()
  print("Successfully added all followers to database")
  return True

#Subsequent runs to track for new followers
def runMonitor(twID):
  ids = get_followingid(twID)
  for id in ids:
    cursor.execute("SELECT EXISTS(SELECT twID FROM followings WHERE twID=?)", (id,))
    if (cursor.fetchone()[0] == 0):
      cursor.execute("INSERT INTO followings VALUES(?)", (id, ))
      userName = get_user(id).screen_name
      sendToDiscord(userName)
      print("User has followed: " + str(userName))

  db.commit()
  return

#Send to discord webhook on new followers, called by runMonitor
def sendToDiscord(userName):
  link = "New followings detected!\n"+"https://twitter.com/" + userName 
  webhook.send(link)

def createDatabase(userID):
  try:
    global db
    db = sqlite3.connect(userID + ".db")
  except Error as e:
    print(e)

  global cursor
  cursor = db.cursor()  


main()!
