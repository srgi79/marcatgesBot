# marcatgesBot
Telegram Bot to record timeworks

## INSTALATION
- Create a python virtual enviorement with ~~~ py -m venv env ~~~
- Install requirements with:
~~~ pip install -r requirements.txt 
~~~
- Copy main.py and edit:
    - **TOKEN**: Telegram Token. Ex: 1111111111:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    - **users_auth**: List of chatid who can use the bot, yours first. Ex: [123456789, 12345678]
        - Create users_auth.json with the list 
- Start the bot with:
~~~ .\env\Scripts\activate 
~~~
~~~ python main.py 
~~~



## RUN AS A SERVICE ##
[Unit]
Description=Telegram Bot Service
Wants=network.target
After=multi-user.target

[Service]
ExecStartPre=/bin/sleep 10
ExecStart=/home/pi/marcatgesBot/env/bin/python /home/pi/marcatgesBot/main.py & >
Restart=always

[Install]
WantedBy=multi-user.target
