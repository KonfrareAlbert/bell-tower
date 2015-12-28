import sys
import json
import datetime
import random

from TwitterAPI import TwitterAPI

class BellTower(object):
    """docstring for BellTower"""
    def __init__(self, credentials_path, data_path):
        # internal data
        self.credentials = self.load_data(credentials_path)
        self.tags = self.load_data(data_path + 'tags.json')
        self.sayings = self.load_data(data_path + 'sayings.json')
        self.time = self.load_data(data_path + 'time.json')

        # TwitterAPI
        self.api = TwitterAPI(
            self.credentials['consumer_key'],
            self.credentials['consumer_secret'],
            self.credentials['access_token_key'],
            self.credentials['access_token_secret']
        )

        # internal attributes
        self.num_tags = 1
        self.num_sayings = 1
        self.periodicity = 15
        self.max_tweet_char = 140

    def load_data(self, path_file):
        data = open(path_file, 'r').read()
        return json.loads(data)

    def tweet(self, date):

        if date.minute % self.periodicity != 0:
            raise Exception('Minutes must be multiple of 15')

        text = ''
        while len(text) <= 0 or len(text) > self.max_tweet_char:
            text = self.process_text(date)

        r = self.api.request('statuses/update', {'status': text})
        print('SUCCESS' if r.status_code == 200 else 'FAILURE')

    def process_text(self, date):

        # build tweet message - hour
        text = self.get_hour(date)

        # build tweet message - saying
        text += '\n%s' % self.get_random_token(self.sayings, date)

        # build tweet message - tag
        text += ' #%s' % self.get_random_token(self.tags, date)

        return text

    def get_hour(self, date):
        # take hour value and parse hour to AM system
        hour = date.hour % 12

        # produce string for time dict
        hour_key = '%s:%s' % (hour, date.minute)
        hour_cat = self.time[hour_key]
        hour_num = str(date).split()[1][:5]

        # hour message
        text = '%s - %s' % (hour_num, hour_cat)
        return text

    def get_random_token(self, tokens, date):

        # get day/month key
        key_day = '%s/%s' % (date.day, date.month)

        if key_day in tokens['day_month'][key_day]:

            keys_list = ['day_month'] * 50 +          \
                        ['other'] * 25 +              \
                        ['month'] * 15 +              \
                        ['day_week'] * 7 +            \
                        ['hours_interval'] * 2 +      \
                        ['calendar_interval'] * 1
        else:

            keys_list = ['other'] * 50 +              \
                        ['month'] * 25 +              \
                        ['day_week'] * 15 +           \
                        ['hours_interval'] * 7 +      \
                        ['calendar_interval'] * 3

        # choode weighted random keys
        key = str(random.choice(keys_list))

        if key == 'day_month':
            key_ = key_day

        elif key == 'month':
            key_ = str(date.month)

        elif key == 'calendar_interval':
            key_ = 'interval_1'

        elif key == 'day_week':
            key_ = str(date.weekday() + 1)

        elif key == 'hours_interval':
            key_ = 'morning'

        # get a random tokens
        if key == 'other':
            tag = random.sample(tokens[key], 1)
        else:
            tag = random.sample(tokens[key][key_], 1)

        return tag[0]

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print '[ERROR] You must provide the path to your Twitter credentials and tags.'
        sys.exit()

    # Get current date
    now = datetime.datetime.now()

    # Instantiate bell tower
    # Internally loads a file with the app credentials,
    # and loads a file with a list of tags to tweet.
    bell = BellTower(sys.argv[1], sys.argv[2])

    # Tweet in twitter given the current date
    bell.tweet(now)