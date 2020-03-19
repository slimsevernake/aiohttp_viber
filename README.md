# aioHTTP Viber
aioHTTP Viber bot is a fully async viber bot written on basis of [Viber REST API](https://developers.viber.com/docs/api/rest-bot-api/).
The purpose of this project is to demonstrate how we at [@baivaru](https://t.me/Baivaru) structures our Viber projects.

You can scan the bellow QR Code to test the demo running bot:\
![.](https://chart.googleapis.com/chart?cht=qr&chl=viber%3A%2F%2Fpa%3FchatURI%3Demain&chs=180x180&choe=UTF-8&chld=L|2)

## Cloning & Run:
1. `git clone https://github.com/eyaadh/aiohttp_viber.git`, to clone and the repository.
2. `cd aiohttp_viber`, to enter the directory.
3. `pip3 install -r requirements.txt`, to install dependencies/requirements.
4. create a new `config.ini` file using the sample available at `viber/working_dir`
5. Run with `python3.8 -m viber`, stop with <kbd>CTRL</kbd>+<kbd>C</kbd>.
> It is recommended to use [virtual environments](https://docs.python-guide.org/dev/virtualenvs/) while running the app, this is a good practice you can use at any of your python projects as virtualenv creates an isolated Python environment which is specific to your project.

The REST API is designed to use webhooks for receiving callbacks and user messages from Viber. For security reasons only URLs with valid and official SSL certificate from a trusted CA is allowed.
In case you wish to test this repo on local you could make use of [ngrok](https://ngrok.com/) and create a public tunnel and use it as the webhook URL(by default the webserver on this project uses port 8080).
> Note that free version of Ngrok expires the public tunnel every 8hrs.


## Viber API & Messaging Flow:
![.](https://developers.viber.com/docs/img/send_and_receive_message_flow.png)
> More details on available Endpoints and API can be found [here](https://developers.viber.com/docs/api/rest-bot-api/).

## Directory Structure:
```
aiohttp_viber/
   └── viber
        ├── utils
        │   ├── api
        │   ├── database
        │   ├── helpers
        │   └── webserver
        └── working_dir

```
#### utils:
The name utils define exactly what this directory is for. All the utilities 
that helps the application to work through is kept in this directory, a module called common 
which loads the required external variables(mostly configurations from configs.ini) and etc.

#### helpers:
Helpers directory consists of modules that connects to 3rd party APIs/sources to help the application gather 
the data it requires. For this demonstration we scrape data and the scraper module is present in this directory.

#### webserver:
This directory consists of the modules that are required for the webhook server that the application uses. 
>In case the webhook server is offline Viber will re-try to deliver the callback until HTTP status code 200 is received. There will be a retry attempt after 5 seconds, and then another after 1 minute and 5 seconds.

#### working_dir:
This directory basically consists of the config.ini file/s. Also if there are temporary files that are generated by the application we tend to leave them 
within this directory at the course of their existence.

#### database:
This directory contains the modules that concerns the DB/RDBMS the application uses. For the purpose of this demonstration I am using TinyDB which is a lightweight document oriented database  
just like MongoDB (which would be my goto DBMS for bigger projects) however you are free to use whichever you prefer. As we use scrapers for the demonstration it is advisable to scrape them data in a schedule basis 
rather than calling the respective scraper whenever a command is received.
>Viber recommends that you record the subscriber ID of each subscriber, as there’s no API for fetching all subscriber IDs for your bot. You can find the subscriber ID in the sender.id property of the “message” callback, or the user.id property of the “subscribed” callback.

#### api:
api consists of modules that deals with viber API.

### Application Workflow:
1. When once a callback from the API is posted to the webhook,  
it calls the function [validate_signature](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/request_sender.py#L29) from the module [ViberApiRequestSender](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/request_sender.py) to validate 
the signature of the JSON that has been received. 
>Each callback will contain a signature on the JSON passed to the callback. The signature is HMAC with SHA256 that will use the authentication token as the key and the JSON as the value. The result will be passed as HTTP Header X-Viber-Content-Signature so the receiver can determine the origin of the message.

2. If the signature is verified it then calls the function [on_event](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/hadlers.py#L14) from the module [ViberHandlers](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/hadlers.py). 
This function looks for the following events:
    - Subscribed: Before an account can send messages to a user, the user will need to subscribe to the account. 
    - Unsubscribed: The user will have the option to unsubscribe from the PA. This will trigger an unsubscribed callback.
    - message: This event is received when the bot account receives any form of [message](https://developers.viber.com/docs/api/rest-bot-api/#message-types).
    
3. If the event is "subscribed", it calls the function [on_subscription](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/hadlers.py#L29) to send a simple welcome message. 
While sending text message the posted json data is as follows:
```
{
   "receiver":"01234567890A=",
   "min_api_version":1,
   "sender":{
      "name":"John McClane",
      "avatar":"http://avatar.example.com"
   },
   "tracking_data":"tracking data",
   "type":"text",
   "text":"Hello world!"
}
```
Module [msg_types](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/msg_types.py) contains these data structures in the form of dictionaries for different [message types](https://developers.viber.com/docs/api/rest-bot-api/#message-types) viber offers and the function 
[prepare_payload](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/commands.py#L72) from the module [commands](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/commands.py) formulates/clean and prepare the required payload for posting.\
When once the payload is ready it calls the function [post](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/request_sender.py#L22) from the module [request_sender](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/request_sender.py).

If the event is "message", it checks whether the message contains tracking data. Tracking data allow the account to track messages and user’s replies. If the bot had sent a message with tracking data - tracking_data value will be passed back with user’s reply (normally used while handling conversation based processes). 
If the message contains tracking data, the trailing process is handled by calling [attend](https://github.com/eyaadh/aiohttp_viber/blob/148403e43cfbc3db693b5e1b3760768d6f72a3bf/viber/utils/api/tracking_data.py#L13) on [tracking_data](https://github.com/eyaadh/aiohttp_viber/blob/master/viber/utils/api/tracking_data.py) module.

If there is no tracking data, it calls the [on_message](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/hadlers.py#L41) function from the module [hadlers](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/hadlers.py). This functions validates received messages for different message types. 
For the purpose of this demonstration we are only checking for text messages and it calls the function [text_validator](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/commands.py#L13) from the module [commands](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/commands.py). 
This function checks whether the received text message is a valid command or otherwise. For this demonstration we use a prefix "!" at the beginning of each command therefore if the message contains the relevant prefix it calls [commands_checker](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/commands.py#L19) from the module 
[commands](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/commands.py) to validate the command and do the trailing process for each respective command.

4. Posting relevant payload to the REST API from the trailing process of a given command is handled by the function [post](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/request_sender.py#l22) from the module 
[request_sender](https://github.com/eyaadh/aiohttp_viber/blob/6e92781c7e4ca001cb2a6aa0e23c91b1e531e528/viber/utils/api/request_sender.py).

## Credits/Mentions of the additional APIs and libraries used with the demonstration:
- [aiohttp](https://pypi.org/project/aiohttp/3.6.2/)
- [aiofiles](https://pypi.org/project/aiofiles/)
- [configparser](https://pypi.org/project/configparser/)
- [bs4](https://pypi.org/project/bs4/)
- [tinydb](https://pypi.org/project/tinydb/)
- [apscheduler](https://pypi.org/project/APScheduler/)
- [unsplash.com](https://unsplash.com/documentation)
- [pixabay.com](https://pixabay.com/api/docs/)
- [FourSquare](https://developer.foursquare.com/docs)

### Project Credits:
[@eyaadh](https://t.me/eyaadh), [@PhoenixAtom](https://t.me/PhoenixAtom) and [@baivaru](https://t.me/BaivaruMedia)


