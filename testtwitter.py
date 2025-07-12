import asyncio
from typing import NoReturn

from twikit import Client, Tweet

from discord_webhook import DiscordWebhook, DiscordEmbed

import requests, re, json, urllib, time
from datetime import datetime
from pprint import pprint as pp

client = Client()

USER_ID = '4291685673'
USERNAME = 'LTAtrafficnews'
CHECK_INTERVAL = 60

WEBHOOK_LINK = '...'


async def get_latest_tweets() -> Tweet:
    return (await client.get_user_tweets(USER_ID, 'Replies'))


async def main() -> NoReturn:
    webhook = DiscordWebhook(url=WEBHOOK_LINK, rate_limit_retry=True,
                            content=f'bot started listening to @{USERNAME}', allowed_mentions={"parse": []})
    response = webhook.execute()

    client.load_cookies('cookies.json')
    before_tweet = (await get_latest_tweets())[0]

    while True:
        to_send = []
        await asyncio.sleep(CHECK_INTERVAL)
        latest_tweets = await get_latest_tweets()
        for latest_tweet in latest_tweets:
            if (
                before_tweet != latest_tweet and
                before_tweet.created_at_datetime < latest_tweet.created_at_datetime
            ):
                try:
                    tweet_id = latest_tweet.id
                    text = latest_tweet.text
                    dt = latest_tweet.created_at_datetime
                    contains = ("Clementi Ave 6" in text) or ("Clementi Avenue 6" in text)
                    # if rate_limit_retry is True then in the event that you are being rate 
                    # limited by Discord your webhook will automatically be sent once the 
                    # rate limit has been lifted
                    webhook = DiscordWebhook(url=WEBHOOK_LINK, rate_limit_retry=True)
                    embed = DiscordEmbed(
                        title="New Post", color=('00ff00' if contains else 'ff0000')
                    )
                    embed.add_embed_field(name="User", value="@"+USERNAME, inline=False)
                    embed.add_embed_field(name="Tweet ID", value=tweet_id, inline=False)
                    embed.add_embed_field(name="Text", value=text, inline=False)
                    embed.add_embed_field(name="Clementi Avenue 6", value=str(contains), inline=False)
                    embed.set_timestamp(dt.timestamp())
                    
                    webhook.add_embed(embed)
                    to_send.append(webhook)
                except Exception as e:
                    webhook = DiscordWebhook(url=WEBHOOK_LINK, rate_limit_retry=True,
                                             content=f'an error occured, {e}', allowed_mentions={"parse": []})
                    webhook.execute()
                    raise e
        before_tweet = latest_tweets[0]
        # send in reverse order so order is chronological
        try:
            for i in reversed(to_send):
                i.execute()
        except Exception as e:
            webhook = DiscordWebhook(url=WEBHOOK_LINK, rate_limit_retry=True,
                                     content=f'an error occured, {e}', allowed_mentions={"parse": []})
            webhook.execute()
            raise e

asyncio.run(main())
