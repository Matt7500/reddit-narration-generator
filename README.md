## Reddit Video Generator

This is my reddit video generator that I worked on from 2020 to late 2021. This is where I learned everything I know now to build the latest version for the story narration program. The biggest difference between the two is this one has a UI for QC checks and the other one doesn't.

This was made to streamline the process of creating the videos for this niche when it was hugely popular back in 2019/2020 after learning of someone who had done something similar, only they used a different language and Python is the one I'm most familiar with so I built it in Python.

## How it works

The program is split into 3 distinct parts. The server, the client, and the video generator. This program was also built to be run on a VPS optionally, just made in a less pretty way.

The project is comprised of three separate programs:

1.  YouTube Bot Server -> initserver.py
2.	YouTube Bot Video Generator Client -> youtubequeue.py
3.	YouTube Bot Client (Manual Review) -> client.py

<h2>YouTube Bot Server</h2>

This program houses the (1) socket server for connecting to the client(s) program and also the (2) socket server for connecting to the video generator client(s). Additionally, this program will also grab new scripts from Reddit every hour, and will also update the existing ones that have not yet been edited.

(1)	This socket server will send raw scripts from the database to the manual review program (see below). It will then receive these reviewed scripts and update the database with the finalised scripts which will include a thumbnail, description and title. The server can handle multiple clients so multiple people can edit these scripts.

(2)	The video generator server is currently only designed to handle one video generator client. The original plans were for this server to handle multiple video generator clients spread out between multiple computers. However, I found that one computer was sufficient enough for all my video generation needs, so I decided to hard code it to only one client. The purpose of this server is to send finalized scripts from the database to the video generator client.

<h2>YouTube Bot Video Generator Client</h2>

This program will receive finalized video scripts from the YouTube Bot Video Generator Server which include thumbnails, descriptions, tags and a title. These scripts will be generated into a mp4 file and then uploaded to YouTube at a scheduled release time.

Once a video is successfully uploaded its status is set to complete along with an upload time so that the program can check how many videos were uploaded within the day to avoid exceeding API quota usage. 

**Text-To-Speech**
This part of the program has been modified many times in this program's time of me using it, first it used balabolka back in 2019 and early 2020. Then, later in 2020, I switched to use AWS for the voices as I found it had higher quality with a very low cost. Then eventually ElevenLabs became the leader in this department and I used it in this program as well as the one that came after.

<h2>YouTube Bot Client</h2>

The client program has a process to filter out comments that are not to be included in the video. It also allows for the user to write the title and upload a thumbnail for the video as well as edit the description and tags, although the title, description and tags are partially generated as follows:
Title: Be default is the post title
Description: By default is a generated template with the post title within it and a couple hashtags
Tags: Some base tags I got from popular text-to-speech channels such as r/askreddit,reddit,reddit funny etc.
All of these can be edited. A template for the thumbnail is partially generated as well. There are checks to make sure that the amount of characters are not exceeded for all of these fields e.g. title must be under 100 characters

The final content of the video includes the edited script, the thumbnail, tags, the description and the video settings (it is possible to change certain features of the video generator template during the editing process such as background colour, text size, line widths etc. I usually kept the defaults so didn’t really have much use for it) which is then sent off to the server which in turn uploads it to the database as a BLOB.

**MySQL**

Storage of the scripts and their relevant information is done with a MySQL database. This is the first time I used a MySQL database for a project, I’m not amazing at SQL, but I learned what was necessary to get things to work. I used three tables “users”, “videogenerators” and “scripts”<br>

**“users” table**<br>
Originally I had planned to create a login system to support multiple users, but this never came to fruition and now its only use is for keeping track of which users are editing which videos to prevent the same video being edited and uploaded twice. Passwords are encrypted with MD5 on the client side

**“scripts” table**<br>
Holds all the script information. The status field is very important for keeping track of where a script should be.
<br>*-raw:* the script is available to edit
<br>*-editing:* the script is being edited and cannot be edited by any other users while in this state
<br>*-complete:* the script has been finished editing and will be sent to the video generator client 
<br>*-successupload:* the script has successfully been uploaded to YouTube

**“videogenerators” table**<br>
Like the users, I designed the client to have a username and password to login. Password is encrypted with MD5 on the client side

These tables will be automatically created within a database called “youtubebot” if they do not already exist.

<h2>Receiving Reddit Scripts</h2>
I used praw to get the Reddit posts (scripts). By default, I have set it to get 100 scripts from the hot tab on r/AskReddit. The minimum number of comments per script must be 1000. It will take 50 of the highest-rated comments from each post, and five of the subsequent highest-rated replies to each comment. The code for this is located in the YouTube Bot Server under reddit.py
Be default on start-up of the YouTube Bot Server, it will request scripts, then it will request every one hour after this. If the script is already in the database it will update the database script entry with the updated comments/upvote values.


Receive credentials for your Google API account will be downloaded and saved automatically following a one-time login (your browser window will be opened requesting a Google account login): videouploader.py -> get_credentials()

## UI Showcase

The UI was built from scratch with PyQT5 and many hours of trial and error to make it look and scale how I wanted. If I were to do this again I would definitely create a web UI but I didn't have that knowledge at this time.

This is an older project so I don't have screenshots for everything but these are the most recent ones of the UI I can find.

**Subreddit selection menu**<br>
This is the menu you're greeted with to choose which subreddit you want to make a video from.
![unknown](https://github.com/user-attachments/assets/b54d8bec-bcbb-4133-b573-3a7ccb45f2c8)

**Video Editor UI**<br>
This is the UI I created to edit and QC the content that will be displayed in the video and an image preview so you know what it will look like in the video as well. (I have censored some of the text due to them not being appropriate)
![EJIgTfr](https://github.com/user-attachments/assets/4f0137b3-6fc8-4af9-8fcf-03525d6ae3bd)

**Video Editor UI comment selector**<br>
This is a later update to the video editor UI that allowed you to see the comments you chose to keep and skip in the program<br>
![unknown](https://github.com/user-attachments/assets/1c5612fa-d45c-4ac2-8ca0-40a3a89c8051)<br>

I really wish I had more pictures of the UI but I only took them while making to show my friends and the video editor part was the main one I was proud of since it took many weeks to build. What is shown in the images isn't the most final version of what the videos looked like since I significantly changed the look of them as well to be just the paragraphs of text over a half-opacity black rectangle on top of a compilation of stock videos.
