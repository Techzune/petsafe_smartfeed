# PetSafe Smart Feed - Python API
Connect and control a PetSafe Smart Feed device using the PetSafe-SmartFeed API.


## Installation
`python setup.py install`


## Login token
You **must** get a login token to use the PetSafe Smart-Feed API.  
There are two methods to retrieve a token:

#### Get token using command line
1. Execute `python -m petsafe_smartfeed [email_address]` to request an email code.
2. Check your email for an email code from PetSafe.
3. Execute `python -m petsafe_smartfeed [email_address] -t [email_code]` to generate a token.

#### Get token using Python
```python
import petsafe_smartfeed as sf

# replace with your email address
email = 'email@example.com'
sf.api.request_code(email)

# check your email for a code
code = input('enter email code (include any dashes): ')
token = sf.api.request_token_from_code(email, code)

print(token)
```


## Example usage
#### List devices
```python
import petsafe_smartfeed as sf

token = 'YOUR TOKEN HERE'
devices = sf.devices.get_feeders(token)

# print all feeders
for device in devices:
    print(device)

```
#### Feed 1/8 cup at normal speed
```python
import petsafe_smartfeed as sf

token = 'YOUR TOKEN HERE'
devices = sf.devices.get_feeders(token)

# get the first feeder
feeder = devices[0]
feeder.feed(amount=1, slow_feed=False)

```
#### Get current battery level (0 - 100)
```python
import petsafe_smartfeed as sf

token = 'YOUR TOKEN HERE'
devices = sf.devices.get_feeders(token)

# get the first feeder
feeder = devices[0]
print(feeder.battery_level)

```
#### Get current food level
```python
import petsafe_smartfeed as sf

token = 'YOUR TOKEN HERE'
devices = sf.devices.get_feeders(token)

# get the first feeder
feeder = devices[0]
status = feeder.food_low_status

if status == 0:
    print('Feeder has food.')
elif status == 1:
    print('Feeder is low on food.')
elif status == 2:
    print('Feeder is out of food.')

```

## Contributing
All contributions are welcome. 
Please, feel free to create a pull request!
