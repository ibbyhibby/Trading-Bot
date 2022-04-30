#CryptoBot
A project created by Ibrahim Daoud to automatically trade crypto at local market extremas.
## Documentation
1. Introduction
    - The purpose of this bot is to trade cryptocurrency (or any digital asset for that matter) <br> 
    and be able to consistently run 24/7 without issue.
    - This bot will receive webhooks from internet sources such as TradingView or other <br>
    internet sources and will send a post request to a Flask app running on Heroku servers. <br> 
    and fulfil the trade via exchanges with the use of API's.
    - Ideally, this bot will do 2 things, generate passive income while securing long term assets <br> 
    a person is holding by buying and selling at local extrema.
    - In simpler terms, in the case of a bear market or in a downtrend, the bot  will convert <br> 
    the asset to a stable asset such as USDT or USDC in the case of cryptocurrency.
      
      
2. Logistics
    - This bot works with the use of; Python, Flask, Heroku (and therefore git), Redis, Gunicorn and a <br> 
    library  containing relevant functions compatible with an exchange's API, such as python-binance or ccxt. 
    - In addition, the bot makes use of various python functions and libraries such as datetime and <br> 
    ZoneInfo which require a Python 3.9.X + runtime.
    - The bot makes use of embedded python threading capabilities to keep the 'infinite' while loop active.   

3. Setting Up
    - To begin, a Heroku client must be initialized. This can be done by creating a free Heroku account, <br>
    and creating a new app. Once this is set up, click on the 'Resources' tab and install Heroku-Redis <br> 
    addon. Additionally, it is best to opt-in for the hobby-dev account ($7 / month) to keep dyno(s) <br> 
    running 24/7. Free plans have dynos that sleep after 30 minutes of inactivity which may cause the <br> 
    2 hour while loop to not complete successfully. An important side note to take note of is to use a <br>
    free service such as uptimerobot.com which will send random (and useless) web requests to the server <br> 
    which will keep sending garbage POST-request with no useful information to keep the dynos active <br>
    on Heroku, which essentially run the code.
   
    - Next, it is important to fill in accurate information in the repo. The following fields must be filled; <br>
    Config.py: API Key, API Secret Key, Webhook Passphrase, <br>
    app.py: The desired cryptocurrency trading pair must be defined so accurate amounts can be <br>
    calculated.
    - Lastly, a Heroku client must be downloaded and set up with a git account on the local machine <br>
    so that the script can be uploaded successfully and work in the cloud rather than a local machine. <br>
    Once this is set up, you may deploy (and re-deploy) your code using the following commands; <br>
    git add .: This initializes the files that will be deployed <br>
    git commit -am "Description goes here": Commits files for changes and leaves a note describing <br> 
    the reason for the updates. <br>
    git push heroku master: Pushes the files to your Heroku web app. <br>
    Note: Other commands also exist and can be found [here]. (https://devcenter.heroku.com/articles/git)
   
4. Creating Webhooks
   - It is now possible to use Tradingview or other internet sources to send webhooks to the newly created <br>
   Heroku webapp. Simply send the webhooks to the URL created on Heroku and ensure the webhooks <br>
   are POST-requests.
   
5. Debugging
   - In the case where Debugging is needed, there is a popular software called [Insomnia] (https://insomnia.rest/) <br>
   which can be used to send webhooks to the Heroku web app. These webhooks can be garbage (fake info) <br>
   or a real order with a very little buy or sell amount (to not accidentally lose funds on debugging). <br>