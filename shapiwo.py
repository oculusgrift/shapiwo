#!/usr/bin/env python3
import logging
from html import unescape, escape
from urllib.parse import quote
from json import load
from typing import Dict, Any

from tweepy import API, Stream, StreamListener, OAuthHandler, Cursor
from tweepy.models import Status

from owo import whats_this

# Config dictionary
config: Dict[str, Any]
# Load config
with open('shapiwo.json', 'r') as file:
  config = load(file)

# Set the logger object at the module level
logger = logging.getLogger(__name__)

# Authenticate with twitter and build API object
logger.info('Authenticating with Twitter')
auth = OAuthHandler(config['auth']['consumer_key'], config['auth']['consumer_secret'])
auth.set_access_token(config['auth']['access_token'], config['auth']['access_secret'])
twitter = API(auth)

def main() -> int:
  # Initialize the logger
  init_logger()

  # Create Twitter Streaming listener
  logger.info('Creating Twitter streaming listener')
  listener = ShapiwoListener()
  stream = Stream(auth=twitter.auth, listener=listener, tweet_mode='extended')

  # Filter the stream on only tweets with user's ID
  logger.info(f'Filtering stream to tweets mentioning User ID {config["user"]["id"]}')
  stream.filter(follow=[config['user']['id']])

  return 0

def init_logger() -> None:
  """ init_logger is a garbage function that sets a logger with owo format """

  # Set up root logger to INFO level and only print the owo'd log message
  logging.basicConfig(
    level=logging.INFO,
    format='%(owo)s')
  
  # Raise the module logger to DEBUG
  logging.getLogger(__name__).setLevel(logging.DEBUG)

  # Get the original log factory
  factory = logging.getLogRecordFactory()

  def owo_factory(*args, **kwargs) -> logging.LogRecord:
    """ owo_factory is a log factory that owos log messages """
    # Run original factory
    record = factory(*args, **kwargs)

    # OwO the provided message and return it
    record.owo = whats_this(record.msg) # type: ignore
    return record
  
  # Set the logger to use the owo factory
  logging.setLogRecordFactory(owo_factory)

class ShapiwoListener(StreamListener):
  """ ShapiwoListener is a Twitter StreamListener that OwOs tweets and reposts them """

  def on_status(self, status: Status) -> None:
    """ on_status acts on a new status in the StreamListener """
    logger.debug(f'Tweet with ID {status.id} received')

    self.handle_tweet(status)

  @classmethod
  def handle_tweet(cls, status: Status) -> None:
    """ handle_tweet decides how to handle an incoming tweet """
    if status.in_reply_to_user_id_str == config['user']['id'] and status.user.id_str == config['user']['id']:
      # If this is a reply to a previous tweet from user and is from user,
      # shitpost to thread
      logger.info(f'What\'s this? A thread tweet from creator with ID {status.id} received')
      cls.screedpiwo(status)

      return
    elif hasattr(status, 'retweeted_status') \
         or status.in_reply_to_status_id != None \
         or status.in_reply_to_screen_name != None \
         or status.in_reply_to_user_id != None:
      return
    else:
      # If this is a tweet from Shapiro, shitpost
      logger.info(f'What\'s this? A tweet from creator with ID {status.id} received')
      cls.shapiwo(status)

      return

  @classmethod
  def status_text(cls, status: Status) -> str:
    """ status_text extracts the text from a given status """
  
    logger.debug('Extracting status text')
    try:
      # Tweets over 140 characters have an extended_tweet attribute when
      # received via the streaming API
      text = status.extended_tweet['full_text']
    except AttributeError:
      try:
        # Tweets over 140 characters have a full_text attribute when received
        # outside of the streaming API
        text = status.full_text
      except AttributeError:
        # Tweets under 140 characters just have a text attribute
        text = status.text
    
    # Unescape the text for realistic char limits (e.g. &nbsp; becomes &)
    return unescape(text)
  
  @classmethod
  def owo_status(cls, status: Status, affixes: bool = True) -> str:
    """ owo_status extracts the text from a status and owos it """

    # Extract status text
    text = cls.status_text(status)

    # Print text to avoid owo formatter
    print(text)

    # OwO and return status text
    return whats_this(text, affixes=affixes)
  
  @classmethod
  def reply_status(cls, status: Status) -> Status:
    """ reply_status finds the shapiwo status that a given non-shapiwo status is in reply to """

    # Get the non-shapiwo status that this is in reply to
    logger.debug('Retrieving root status')
    root_status = twitter.get_status(status.in_reply_to_status_id, tweet_mode='extended')

    # OwO the non-shapiwo status text WITHOUT affixes, since they are random
    logger.debug('Retrieving OwO\'d version of root status')
    owo = cls.owo_status(root_status, affixes=False)

    # Print the OwO text
    print(owo)

    # Scroll through the 100 most recent tweets from shapiwo
    for status in Cursor(twitter.user_timeline, id=config['bot']['id'], tweet_mode='extended').items(100):
      # If the current shapiwo status contains the OwO'd text with no prefixes,
      # return it
      if owo in cls.status_text(status):
        return status
    
    # Raise an error if it couldn't be found
    raise ValueError(f'Unable to find root status for thread reply {root_status.id}')
  
  @classmethod
  def screedpiwo(cls, status: Status) -> None:
    """ screedpiwo handles a threaded tweet """

    # Retrieve the shapiwo reply status for a given root tweet
    logger.info('Getting reply status')
    try:
      reply_status = cls.reply_status(status)
    except ValueError as e:
      # Skip if not found
      logger.error(f'Skipping: {e}')
      return
    
    # Post the new shapiwo'd tweet as a reply to the found root
    cls.shapiwo(status, reply_status)

  @classmethod
  def shapiwo(cls, status: Status, reply_status: Status = None) -> None:
    """ shapiwo takes a tweet, owos it, and tweets it """

    # OwO the status
    owo = cls.owo_status(status)

    # Build URL to original tweet
    url = f'https://twitter.com/{status.user.screen_name}/status/{status.id}'

    if len(f'{owo} {url}') <= 280:
      # If we can add a link and still be within the char limit, add it
      owo = f'{owo} {url}'

    # Print and tweet the owo'd status
    print(owo)

    if reply_status is not None:
      # If a reply status is supplied, reply to it
      logger.info(f'Tweeting reply to status {status.id}')
      twitter.update_status(
        owo,
        in_reply_to_status_id=reply_status.id,
        auto_populate_reply_metadata=True
      )
    else:
      # Otherwise, post a new tweet
      logger.info('Tweeting new status')
      twitter.update_status(owo)

if __name__ == '__main__':
  # Run script
  exit(main())
