# PetSafe Smart Feed - Python API
Connect and control a PetSafe Smart Feed device using the PetSafe-SmartFeed API.

> **BREAKING CHANGE:** Version 2.0 uses the new PetSafe API.
> You will need to request new tokens.

> PetSafe will lock your account if you request data more often than once per 5 minutes.

## Installation
`pip install petsafe-smartfeed`

If installing from source code,
`python setup.py install`

## Login tokens
You **must** use tokens to interact with the PetSafe Smart-Feed API.  
There are two methods to retrieve tokens:

#### Get tokens using command line
1. Execute `python -m petsafe_smartfeed [email_address]` to request an email code.
2. Check your email for an email code from PetSafe.
3. Enter your code to generate tokens.

#### Get tokens using Python
```python
import petsafe_smartfeed as sf


# replace with your email address
client = sf.PetSafeClient(email="email@example.com")
client.request_code()

# check your email for a code
code = input("Enter email code: ")
token = client.request_tokens_from_code(code)

print("email:", client.email)
print("id_token:", client.id_token)
print("refresh_token:", client.refresh_token)
print("access_token:", client.access_token)
```


## Example usage
#### List feeders

```python
import petsafe_smartfeed as sf

client = sf.PetSafeClient(email="email@example.com",
                       id_token="YOUR_ID_TOKEN",
                       refresh_token="YOUR_REFRESH_TOKEN",
                       access_token="YOUR_ACCESS_TOKEN")
feeders = client.feeders

# print all feeders
for feeder in feeders:
    print(feeder)

```
#### Feed 1/8 cup at normal speed
```python
import petsafe_smartfeed as sf

client = sf.PetSafeClient(email="email@example.com",
                       id_token="YOUR_ID_TOKEN",
                       refresh_token="YOUR_REFRESH_TOKEN",
                       access_token="YOUR_ACCESS_TOKEN")
feeders = client.feeders

# get the first feeder
feeder = feeders[0]
feeder.feed(amount=1, slow_feed=False)

```
#### Get current battery level (0 - 100)
```python
import petsafe_smartfeed as sf

client = sf.PetSafeClient(email="email@example.com",
                       id_token="YOUR_ID_TOKEN",
                       refresh_token="YOUR_REFRESH_TOKEN",
                       access_token="YOUR_ACCESS_TOKEN")
feeders = client.feeders

# get the first feeder
feeder = feeders[0]
print(feeder.battery_level)

```
#### Get current food level
```python
import petsafe_smartfeed as sf

client = sf.PetSafeClient(email="email@example.com",
                       id_token="YOUR_ID_TOKEN",
                       refresh_token="YOUR_REFRESH_TOKEN",
                       access_token="YOUR_ACCESS_TOKEN")
feeders = client.feeders

# get the first feeder
feeder = feeders[0]
status = feeder.food_low_status

if status == 0:
    print("Feeder has food.")
elif status == 1:
    print("Feeder is low on food.")
elif status == 2:
    print("Feeder is out of food.")

```

## Contributing
All contributions are welcome. 
Please, feel free to create a pull request!
