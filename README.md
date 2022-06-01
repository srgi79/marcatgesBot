# marcatgesBot
Telegram Bot to record timeworks

## INSTALATION
- Create a python virtual enviorement with:
~~~ 
py -m venv env 
~~~
- Install requirements with:
~~~ 
pip install -r requirements.txt 
~~~
- Copy main.py and edit:
    - **TOKEN**: Telegram Token. Ex: 1111111111:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    - **users_auth**: List of chatid who can use the bot, yours first. Ex: [] [123456789, 12345678]
        - Create users_auth.json with the list 
- Start the bot with:
~~~ 
.\env\Scripts\activate 
~~~
~~~ 
python main.py 
~~~



## RUN AS A SERVICE IN RPI ##
- Copy **marcatges.service** in **/lib/systemd/system** folder
- Reaload systemd:
~~~
sudo systemctl daemon-reload
~~~
- Start service:
~~~
sudo systemctl start marcatges.service 
~~~
- If it works, enable the service on boot:
~~~
sudo systemctl enable marcatges.service 
~~~

