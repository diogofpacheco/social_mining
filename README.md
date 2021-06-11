# Usage
The following code is used to gather tweets using the streaming API. These are the steps:

 1. Clone this repo to your environment
 2. Install the dependencies
 3. Run the script. The config file should be in social_mining/res/config/ folder.
 4. The script will run indefinetely, listening to Twitter and copying them whenever they match your [criteria](#configuration). Every day, a new file will be created. Ctrl+C to stop the application.
```
git clone git@github.com:diogofpacheco/social_mining.git
pip3 install twitter --user
pip3 install configobj --user
cd social_mining/src/
python3 streamtweets.py --config=termsToTrack.txt
```
# Configuration

In the [configuration file](https://github.com/diogofpacheco/social_mining/blob/main/res/config/config-example.txt), you specify the general parameters of of scripts:
```
# Twitter keys
api_key = '<add_yours>'
api_secret = '<add_yours>'
access_token_key = '<add_yours>'
access_token_secret = '<add_yours>'
# Files
debugFilename = 'myDebug.log'
termsFilename = 'termsToTrack.txt'
# Storage Path - make sure the directory is created before executing the script
output_path = '/nobackup/pacheco/tweets'
# the name of the ouputjson with the daily tweets. Files will be created per day and it will have the date appended to the basename
base_filename = 'twitter_stream-'
# GEO - BB Brasil
#boundingBox = '-74.0020507813,-33.7421875,-34.80546875,5.25795898437'
boundingBox = 
```

In [terms to track](https://github.com/diogofpacheco/social_mining/blob/main/res/terms/termsToTrack.txt) should have the following format. You can specify terms in using the `track` field and/or accounts using the `follow` field.
```
# list of terms to query tweets. Similar to using the web search field. It will match a tweet text or any other metadata in user profile.
track = "#TermsToTrackTest, @diogofpacheco"
# list of account_ids. It will track all tweets performed by these accounts and also any mention to them.
follow = "221381860"
```

