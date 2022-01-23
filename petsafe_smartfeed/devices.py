import json
from . import api


def get_feeders(token):
    """
    Sends a request to PetSafe's API for all feeders associated with account.

    :param token: the access token for the account
    :return: list of Feeders

    """
    response = api.sf_get('feeders', token)
    response.raise_for_status()
    content = response.content.decode('UTF-8')
    return [DeviceSmartFeed(token, feeder_data) for feeder_data in json.loads(content)]


class DeviceSmartFeed:
    def __init__(self, token, data):
        self.token = token
        self.data = data

    def __str__(self):
        return self.to_json()

    def to_json(self):
        """
        All feeder data formatted as JSON.

        """
        return json.dumps(self.data, indent=2)

    def update_data(self):
        """
        Updates self.data to the feeder's current online state.

        """
        response = api.sf_get(self.api_path, token=self.token)
        response.raise_for_status()
        self.data = json.loads(response.content.decode('UTF-8'))

    def put_setting(self, setting, value, force_update=False):
        """
        Changes the value of a specified setting. Sends PUT to API.

        :param setting: the setting to change
        :param value: the new value of that setting
        :param force_update: if True, update ALL data after PUT. Defaults to False.

        """
        response = api.sf_put(self.api_path + 'settings/' + setting, token=self.token, data={
            'value': value
        })
        response.raise_for_status()

        if force_update:
            self.update_data()
        else:
            self.data['settings'][setting] = value

    def get_messages_since(self, days=7):
        """
        Requests all feeder messages.

        :param days: how many days to request back. Defaults to 7.
        :return: the APIs response in JSON.

        """
        response = api.sf_get(self.api_path + 'messages?days=' + str(days), token=self.token)
        response.raise_for_status()
        return json.loads(response.content.decode('UTF-8'))

    def get_last_feeding(self):
        """
        Finds the last feeding in the feeder's messages.

        :return: the feeding message, if found. Otherwise, None.

        """
        messages = self.get_messages_since()
        for message in messages:
            if message['message_type'] == 'FEED_DONE':
                return message
        return None

    def feed(self, amount=1, slow_feed=None, update_data=True):
        """
        Triggers the feeder to begin feeding.

        :param amount: the amount to feed in 1/8 increments.
        :param slow_feed: if True, will use slow feeding. If None, defaults to current settings.
        :param update_data: if True, will update the feeder's data after feeding. Defaults to True.

        """
        if slow_feed is None:
            slow_feed = self.data['settings']['slow_feed']
        response = api.sf_post(self.api_path + 'meals', self.token, data={
            'amount': amount,
            'slow_feed': slow_feed
        })
        response.raise_for_status()

        if update_data:
            self.update_data()

    def repeat_feed(self):
        """
        Repeats the last feeding.

        """
        last_feeding = self.get_last_feeding()
        self.feed(last_feeding['amount'])

    def prime(self):
        """
        Feeds 5/8 cups to prime the feeder.

        """
        self.feed(5, False)

    def schedule_feed(self, time="00:00", amount=1, update_data=True):
        """
        Adds time and feed amount to schedule.
        
        :param time: the time to dispense the food in 24 hour notation with colon separation (e.g. 16:35 for 4:35PM)
        :param amount: the amount to feed in 1/8 increments.
        :param update_data: if True, will update the feeder's data after feeding. Defaults to True.

        """
        response = api.sf_post(self.api_path + 'schedules', self.token, data={
            'time': time,
            'amount': amount
        })
        response.raise_for_status()

    def delete_schedule(self, schedule_id, update_data=True):
        """
        Deletes specified schedule.
        
        :param schedule_id: the id of the scheduled feed to delete (six digits as of writing)
        :param update_data: if True, will update the feeder's data after feeding. Defaults to True.

        """
        response = api.sf_delete(self.api_path + 'schedules/' + schedule_id, self.token)
        response.raise_for_status()
    
    def delete_all_schedules(self, update_data=True):
        """
        Deletes all schedules.
        
        :param update_data: if True, will update the feeder's data after feeding. Defaults to True.

        """
        response = api.sf_delete(self.api_path + 'schedules', self.token)
        response.raise_for_status()        
        
    @property
    def api_name(self):
        """The feeder's thing_name from the API."""
        return self.data['thing_name']

    @property
    def api_path(self):
        """The feeder's path on the API."""
        return 'feeders/' + self.api_name + '/'

    @property
    def id(self):
        """The feeder's ID."""
        return self.data['id']

    @property
    def battery_voltage(self):
        """The feeder's calculated current battery voltage."""
        try:
            return round(int(self.data['battery_voltage']) / 32767 * 7.2, 3)
        except ValueError:
            return -1

    @property
    def battery_level(self):
        """
        The feeder's current battery level on a scale of 0-100.
        Returns 0 if no batteries installed.

        """
        if not self.data['is_batteries_installed']:
            return 0
        minVoltage = 22755
        maxVoltage = 29100
        return round(max((100 * (int(self.data['battery_voltage']) - minVoltage)) / (maxVoltage - minVoltage), 0))

    @property
    def paused(self):
        """If true, the feeder will not follow its scheduling."""
        return self.data['settings']['paused']

    @paused.setter
    def paused(self, value):
        self.put_setting('paused', value)

    @property
    def slow_feed(self):
        """If true, the feeder will dispense food slowly."""
        return self.data['settings']['slow_feed']

    @slow_feed.setter
    def slow_feed(self, value):
        self.put_setting('slow_feed', value)

    @property
    def child_lock(self):
        """If true, the feeder's physical button is disabled."""
        return self.data['settings']['child_lock']

    @child_lock.setter
    def child_lock(self, value):
        self.put_setting('child_lock', value)

    @property
    def friendly_name(self):
        """The feeder's display name."""
        return self.data['settings']['friendly_name']

    @friendly_name.setter
    def friendly_name(self, value):
        self.put_setting('friendly_name', value)

    @property
    def pet_type(self):
        """The feeder's pet type."""
        return self.data['settings']['pet_type']

    @pet_type.setter
    def pet_type(self, value):
        self.put_setting('pet_type', value)

    @property
    def food_sensor_current(self):
        """The feeder's food sensor status."""
        return self.data['food_sensor_current']

    @property
    def food_low_status(self):
        """
        The feeder's food low status.

        :return: 0 if Full, 1 if Low, 2 if Empty

        """
        return int(self.data['is_food_low'])
