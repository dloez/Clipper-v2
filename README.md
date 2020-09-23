# Clipper

Clipper is a tool made to automate the whole process of downloading twitch clips from a content creator, process, concatenate, edit and upload to youtube.
It integrates Twitch API, YouTube API, and Google Cloud to automate the whole process.

## How it works
Clipper has all the code in different modules. All modules have it's own commander function that reads user input and dispatch actions. Thanks to the use of modules you can scale the bot as far as you want, all you need to do is create a new module with your new commands prepared and clipper will pass new commands to it.

1. Clipper uses a "video packer manager" to collect all the data it needs to automate each step. It asks the user to enter the content creator twitch name, the folder where the thumbnails are stored, etc. Each clipper module will need a package name as an argument to process.

2. Downloader module will take the content creator name from the package and download the last x clips from twitch. The number of clips is also described in the package.

3. Encoder module will re-encode downloaded clips to match the same encode params to avoid future errors.

4. Editor module will concatenate all clips plus a custom intro and outro into a single mp4 file, the final video.

5. Uploader module will upload the video to google cloud storage and to YouTube using [YoutubeUploader](https://github.com/porjo/youtubeuploader).

The rest of the modules takes care of user-friendly commands like 'exit', scheduling a set of videos for each day of the week or purging video clips, or already uploaded videos from the local machine.

## Disclaimer
This project is no longer maintained (well it was never maintained tbh). I just made it as a joke to a friend who thought that the process of uploading other content creator's content was "hard" just because you need to see a bunch of clips. I won't add steps to install it into a server just in case someone wants to use it to its benefit.