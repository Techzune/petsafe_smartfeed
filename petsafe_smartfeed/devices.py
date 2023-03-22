import json
from warnings import warn


def get_feeders(client):
    """
    Sends a request to PetSafe for all feeders associated with an account.

    .. deprecated:: 2.3
              `get_feeders` will be removed in the next version.
              Use `PetSafeClient.feeders` instead.

    Parameters
    ----------
    client : PetSafeClient
        Authorized PetSafe client

    Returns
    -------
    list of DeviceSmartFeed

    """
    warn(
        "`get_feeders` will be removed in the next version. Use `PetSafeClient.feeders` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    response = client.api_get("feeders")
    response.raise_for_status()
    content = response.content.decode("UTF-8")
    return [DeviceSmartFeed(client, feeder_data) for feeder_data in json.loads(content)]


class DeviceSmartFeed:
    def __init__(self, client, data):
        """
        PetSafe SmartFeed device.

        Parameters
        ----------
        client : PetSafeClient
            Authorized PetSafe client
        data : dict
            PetSafe's provided JSON feeder data

        Notes
        -----
        It is recommended you retrieve this using `PetSafeClient.feeders`.

        """
        self.client = client
        self.data = data

    def __str__(self):
        """
        An alias of `to_json`.

        """
        return self.json

    @property
    def json(self):
        """
        Feeder data formatted as JSON.

        """
        return json.dumps(self.data, indent=2)

    def update_data(self):
        """
        Updates `self.data` to the feeder's current state from PetSafe.

        """
        response = self.client.api_get(self.api_path)
        response.raise_for_status()
        self.data = json.loads(response.content.decode("UTF-8"))

    def put_setting(self, setting, value, force_update=False):
        """
        Changes a value of the feeder's settings.

        Parameters
        ----------
        setting : str
            Name of setting to be changed
        value
            Value of setting to apply
        force_update : bool, optional
            If True, updates ALL device data after PUT.
            Defaults to False.

        """
        response = self.client.api_put(
            self.api_path + "settings/" + setting,
            data={
                "value": value,
            },
        )
        response.raise_for_status()

        if force_update:
            self.update_data()
        else:
            self.data["settings"][setting] = value

    def get_messages_since(self, days=7):
        """
        Requests feeder messages since a specified date.

        Parameters
        ----------
        days : int, optional
            Number of days to request back.
            Default to 7.

        Returns
        -------
        dict
            JSON data returned from PetSafe

        """
        response = self.client.api_get(self.api_path + "messages?days=" + str(days))
        response.raise_for_status()
        return json.loads(response.content.decode("UTF-8"))

    def get_last_feeding(self):
        """
        Requests the most recent feeding message within past 7 days.

        Returns
        -------
        dict or None
            JSON data returned from PetSafe

        """
        messages = self.get_messages_since()
        for message in messages:
            if message["message_type"] == "FEED_DONE":
                return message
        return None

    def feed(self, amount=1, slow_feed=None, update_data=True):
        """
        Requests the feeder to start a feeding.

        Parameters
        ----------
        amount : int
            Amount to feed in increments of 1/8
        slow_feed : bool, optional
            If True, will use slow feeding.
            Defaults to current setting.
        update_data : bool
            If True, updates ALL device data after the request.
            Defaults to True.

        """
        if slow_feed is None:
            slow_feed = self.data["settings"]["slow_feed"]

        response = self.client.api_post(
            self.api_path + "meals",
            data={
                "amount": amount,
                "slow_feed": slow_feed,
            },
        )
        response.raise_for_status()

        if update_data:
            self.update_data()

    def repeat_feed(self):
        """
        Repeats the last feeding.

        """
        last_feeding = self.get_last_feeding()
        self.feed(last_feeding["amount"])

    def prime(self):
        """
        Feeds 5/8 cups to prime the feeder.

        """
        self.feed(5, False)

    def get_schedules(self):
        """
        Requests all scheduled feeds.

        Returns
        -------
        dict
            JSON data returned from PetSafe

        """
        response = self.client.api_get(self.api_path + "schedules")
        response.raise_for_status()
        return json.loads(response.content.decode("UTF-8"))

    def schedule_feed(self, time="00:00", amount=1, update_data=True):
        """
        Adds scheduled feed with time and food amount.

        .. deprecated:: 2.3
                  `schedule_feed` will be removed in the next version.
                  Use `add_schedule` instead.

        Parameters
        ----------
        time : str
            Time to dispense the food in 24 hour notation with colon separation (e.g. 16:35 for 4:35PM)
        amount : int
            Amount to feed in increments of 1/8
        update_data
            If True, updates ALL device data after the request.
            Defaults to True.

        Returns
        -------
        dict
            JSON data returned from PetSafe
            (Unique ID of the scheduled feed)

        """
        warn(
            "`schedule_feed` will be remvoved in the next version. Use `add_schedule` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_schedule(time, amount, update_data)

    def add_schedule(self, time="00:00", amount=1, update_data=True):
        """
        Adds scheduled feed with time and food amount.

        Parameters
        ----------
        time : str
            Time to dispense the food in 24 hour notation with colon separation (e.g. 16:35 for 4:35PM)
        amount : int
            Amount to feed in increments of 1/8
        update_data
            If True, updates ALL device data after the request.
            Defaults to True.

        Returns
        -------
        dict
            JSON data returned from PetSafe
            (Unique ID of the scheduled feed)

        """
        response = self.client.api_post(
            self.api_path + "schedules",
            data={
                "time": time,
                "amount": amount,
            },
        )
        response.raise_for_status()

        if update_data:
            self.update_data()

        return json.loads(response.content.decode("UTF-8"))

    def modify_schedule(self, time="00:00", amount=1, schedule_id="", update_data=True):
        """
        Modifies the food amount and time of the specified scheduled feed ID.

        Parameters
        ----------
        time : str
            Time to dispense the food in 24 hour notation with colon separation (e.g. 16:35 for 4:35PM)
        amount : int
            Amount to feed in increments of 1/8
        schedule_id : str
            Unique ID of the schedule to modify
        update_data
            If True, updates ALL device data after the request.
            Defaults to True.

        """
        response = self.client.api_put(
            self.api_path + "schedules/" + schedule_id,
            data={
                "time": time,
                "amount": amount,
            },
        )
        response.raise_for_status()

        if update_data:
            self.update_data()

    def delete_schedule(self, schedule_id="", update_data=True):
        """
        Deletes the specified scheduled feed ID.

        Parameters
        ----------
        schedule_id : str
            Unique ID of the schedule to modify
        update_data
            If True, updates ALL device data after the request.
            Defaults to True.

        """
        response = self.client.api_delete(self.api_path + "schedules/" + schedule_id)
        response.raise_for_status()

        if update_data:
            self.update_data()

    def delete_all_schedules(self, update_data=True):
        """
        Deletes all scheduled feeds.

        Parameters
        ----------
        update_data
            If True, updates ALL device data after the request.
            Defaults to True.

        """
        response = self.client.api_delete(self.api_path + "schedules")
        response.raise_for_status()

        if update_data:
            self.update_data()

    @property
    def api_name(self):
        """
        Feeder's thing_name from the API.

        """
        return self.data["thing_name"]

    @property
    def api_path(self):
        """
        Feeder's path on the API.

        """
        return "feeders/" + self.api_name + "/"

    @property
    def id(self):
        """
        Feeder's ID.

        """
        return self.data["id"]

    @property
    def battery_voltage(self):
        """
        Feeder's calculated current battery voltage.

        """
        try:
            return round(int(self.data["battery_voltage"]) / 32767 * 7.2, 3)
        except ValueError:
            return -1

    @property
    def battery_level(self):
        """
        Feeder's current battery level on a scale of 0-100.
        Will return 0 if no batteries installed.

        """
        if not self.data["is_batteries_installed"]:
            return 0
        minVoltage = 22755
        maxVoltage = 29100
        return round(
            max(
                (100 * (int(self.data["battery_voltage"]) - minVoltage))
                / (maxVoltage - minVoltage),
                0,
            )
        )

    @property
    def paused(self):
        """
        If True, the feeder will not follow its scheduling.

        Setting this property automatically updates via the API.
        This does not update ALL device data.

        """
        return self.data["settings"]["paused"]

    @paused.setter
    def paused(self, value):
        self.put_setting("paused", value)

    @property
    def slow_feed(self):
        """
        If true, the feeder will dispense food slowly.

        Setting this property changes the setting via the API.
        This does not update ALL device data.

        """
        return self.data["settings"]["slow_feed"]

    @slow_feed.setter
    def slow_feed(self, value):
        self.put_setting("slow_feed", value)

    @property
    def child_lock(self):
        """
        If true, the feeder's physical button is disabled.

        Setting this property changes the setting via the API.
        This does not update ALL device data.

        """
        return self.data["settings"]["child_lock"]

    @child_lock.setter
    def child_lock(self, value):
        self.put_setting("child_lock", value)

    @property
    def friendly_name(self):
        """
        The feeder's display name.

        Setting this property changes the setting via the API.
        This does not update ALL device data.

        """
        return self.data["settings"]["friendly_name"]

    @friendly_name.setter
    def friendly_name(self, value):
        self.put_setting("friendly_name", value)

    @property
    def pet_type(self):
        """
        Feeder's pet type.

        Setting this property changes the setting via the API.
        This does not update ALL device data.

        """
        return self.data["settings"]["pet_type"]

    @pet_type.setter
    def pet_type(self, value):
        self.put_setting("pet_type", value)

    @property
    def food_sensor_current(self):
        """
        Feeder's food sensor status.

        """
        return self.data["food_sensor_current"]

    @property
    def food_low_status(self):
        """
        Feeder's food low status.
        (0 if Full, 1 if Low, 2 if Empty)

        """
        return int(self.data["is_food_low"])
