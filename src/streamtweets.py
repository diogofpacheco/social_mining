from twitter import *
from collections import deque
from threading import Thread
import json
import logging
import time
from configobj import ConfigObj
import sys,getopt,os, inspect
curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/'

class RotatingFileOpener():
    def __init__(self, path, mode='a+', prepend="", append=""):
        if not os.path.isdir(path):
            raise FileNotFoundError("Can't open directory '{}' for data output.".format(path))
        self._path = path
        self._prepend = prepend
        self._append = append
        self._mode = mode
        self._day = time.localtime().tm_mday
    def __enter__(self):
        self._filename = self._format_filename()
        self._file = open(self._filename, self._mode)
        return self
    def __exit__(self, *args):
        return getattr(self._file, '__exit__')(*args)
    def _day_changed(self):
        return self._day != time.localtime().tm_mday
    def _format_filename(self):
        return os.path.join(self._path, "{}{}{}".format(self._prepend, time.strftime("%Y%m%d"), self._append))
    def write(self, *args):
        if self._day_changed():
            self._file.close()
            self._file = open(self._format_filename(), self._mode)
        return getattr(self._file, 'write')(*args)
    def __getattr__(self, attr):
        return getattr(self._file, attr)
    def __iter__(self):
        return iter(self._file)

def main(argv):
    try:                                
        opts, args = getopt.getopt(argv, "c:", ['config='])
        if not opts:
            print('Inform config file using -c or --config.')
            sys.exit(2) 
    except getopt.GetoptError:          
        sys.exit(2) 
        
    for opt, arg in opts:                
        if opt in ("-c", "--config"):                
            configFile = curdir + '../res/config/' + arg           
    
    # loading config file
    config = ConfigObj(configFile)
    
    # Configure logging facility
    # - overwrite previous logging files
    # - don't save INFO messages
    # - format example: WARNING: 2014-08-26 14:18:41,626 limit 2
    logging.basicConfig(filename=curdir + '../res/config/' + config['debugFilename'],filemode='w',format='%(levelname)s: %(asctime)s %(message)s',level=logging.INFO)
    
    api_key = config['api_key']
    api_secret = config['api_secret']
    access_token_key = config['access_token_key']
    access_token_secret = config['access_token_secret']
    output_path = config['output_path']
    base_filename = config['base_filename']
    
    # Authenticate the application to use Twitter API
    #rest = Twitter(auth=OAuth(access_token_key, access_token_secret, 
    #    			api_key, api_secret))
    
    stream = TwitterStream(auth=OAuth(access_token_key, access_token_secret, 
        			api_key, api_secret))
    
    
    # if Twitter disconnect us, try to recconect as soon as possible
    with RotatingFileOpener(output_path, prepend=base_filename, append='.json') as logger:
        while True:
            try:
                # loading terms file
                termsObj = ConfigObj(curdir + '../res/terms/' + config['termsFilename'])
                
                ## load terms (tags, names) to be tracked
                tags = termsObj['track'] + ((', ' + termsObj['extra_track']) if termsObj['extra_track'] else '')
                profiles = termsObj['follow'] + ((', ' + termsObj['extra_follow']) if termsObj['extra_follow'] else '')
            
                ## set the bounding box
                if config['boundingBox']:
                    boundingBox = config['boundingBox']
                else:    
                    boundingBox = ""
            #         for countryBB in [c.bbox for c in country_subunits_by_iso_code('GB')]:
            #             boundingBox += str(countryBB) + ','
            #         boundingBox = boundingBox[:-1].replace('(','').replace(')','').replace(' ','')
                
                # boundingBox = '-80.727032, 28.017660, -80.547817, 28.212670' 
                
                print("Starting Tracking at " + time.ctime(time.time()))
        ### preparing tracking parameters
                if tags:
                    if profiles:
                        print('\tProfiles: ',profiles)
                        print('\tTerms: ',tags)
                        cursor = stream.statuses.filter(track=tags
                                            ,follow=profiles
                                            ,locations=boundingBox
                                            ,stall_warnings='true')
                    else:
                        print('\tTerms: ',tags)
                        cursor = stream.statuses.filter(track=tags
                                            ,locations=boundingBox
                                            ,stall_warnings='true')
                else:
                    if profiles:
                        print('\tProfiles: ',profiles)
                        cursor = stream.statuses.filter(follow=profiles
                                            ,locations=boundingBox
                                            ,stall_warnings='true')
                    else:
                        print('\tNO Terms or Profiles: ')
                        cursor = stream.statuses.filter(locations=boundingBox
                                            ,stall_warnings='true')

                for tweet in cursor:
                
                # 1 - look for normal Tweets
                    if 'coordinates' in tweet:
                        try:
                            # changing from mongo to file
                            #  collection.insert(tweet)
                            logger.write('%s\n' % json.dumps(tweet))
    #                         pass
                        except Exception as ex:
                            print(ex)
                    # 2 - look for Stall Warnings
                    elif 'warning' in tweet:
                        logging.warning('{m} {n}'.format(m=tweet['warning']['code'], n=tweet['warning']['percent_full']))
                    # 3 - look for Limit Notices
                    # These messages indicate that a filtered stream has matched more Tweets than its current rate limit allows to be delivered. 
                    # Limit notices contain a total count of the number of undelivered Tweets since the connection was opened.
                    # Note that the counts do not specify which filter predicates undelivered messages matched.
                    elif 'limit' in tweet:
                        logging.warning('limit {m}'.format(m=tweet['limit']['track']))
                    # 4 - look for Disconnect Messages
                    # Streams may be shut down for a variety of reasons. 
                    # The streaming API will attempt to deliver a message indicating why a stream was closed. 
                    # Note that if the disconnect was due to network issues or a client reading too slowly, it is possible that this message will not be received.
                    elif 'disconnect' in tweet:
                        logging.warning('disconnect {m}'.format(m=tweet['disconnect']['reason']))
                    
            except TwitterHTTPError as e:
                logging.error('{code} {m}'.format(code=e.e.code,m=e.e.reason))
                if 'errors' in e.response_data:
                    e = json.loads(e.response_data)
                    logging.error('{code} {m}'.format(code=e['errors'][0]['code'], m=e['errors'][0]['message']))
            except Exception as ex:
                logging.exception('Unexpected Error')
                # go out of the while loop, something wrong is happening
        #     logTweets.close()
        #     break
        print("End Tracking at " + time.ctime(time.time()))
            # END-try:
        # END-While

if __name__ == '__main__':
    main(sys.argv[1:])



