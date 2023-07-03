from discord_webhook import DiscordWebhook, DiscordEmbed

import requests, re, json, urllib, time
from datetime import datetime
from pprint import pprint

def parse_content(d):
    text = d["content"]["tweet"]["full_text"]
    tweet_id = "@"+d["content"]["tweet"]["id_str"]
    user = "@"+d["content"]["tweet"]["user"]["name"]
    dt = datetime.strptime(d["content"]["tweet"]["created_at"],
                             "%a %b %d %X %z %Y")
    return {"id": tweet_id, "text": text, "user": user, "timestamp": dt.isoformat()}

if __name__ == '__main__':
    USERNAME = "LTAtrafficnews"
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/URL', rate_limit_retry=True,
                            content=f'bot started listening to @{USERNAME}', allowed_mentions={"parse": []})
    response = webhook.execute()

    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{USERNAME}"
    latest = None

    # make an initial request
    with urllib.request.urlopen(url) as response:
        encoding = response.info().get_param('charset', 'utf8')
        html = response.read().decode(encoding)
        result = re.search('script id="__NEXT_DATA__" type="application\\/json">([^>]*)<\/script>', html)[1]

        resp = json.loads(result)["props"]["pageProps"]["timeline"]["entries"]
        latest = parse_content(resp[0])

    # repeat every 5 minutes
    while True:
        time.sleep(300)

        # make another request
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_param('charset', 'utf8')
            html = response.read().decode(encoding)
            result = re.search('script id="__NEXT_DATA__" type="application\\/json">([^>]*)<\/script>', html)[1]

            resp = json.loads(result)["props"]["pageProps"]["timeline"]["entries"]

            # send out messages until latest is hit
            for i in resp:
                if parse_content(i) == latest:
                    latest = parse_content(resp[0])
                    break
                data = parse_content(i)
                try:
                    username = data['user']
                    tweet_id = data['id']
                    text = data['text']
                    dt = datetime.fromisoformat(data["timestamp"])
                    contains = ("Clementi Ave 6" in text) or ("Clementi Avenue 6" in text)
                    # if rate_limit_retry is True then in the event that you are being rate 
                    # limited by Discord your webhook will automatically be sent once the 
                    # rate limit has been lifted
                    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/URL', rate_limit_retry=True)
                    embed = DiscordEmbed(
                        title="New Post", color=('00ff00' if contains else 'ff0000'), timestamp=dt
                    )
                    embed.add_embed_field(name="User", value=username, inline=False)
                    embed.add_embed_field(name="Tweet ID", value=tweet_id, inline=False)
                    embed.add_embed_field(name="Text", value=text, inline=False)
                    embed.add_embed_field(name="Clementi Avenue 6", value=str(contains), inline=False)
                    
                    webhook.add_embed(embed)
                    response = webhook.execute()
                except Exception as e:
                    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/URL', rate_limit_retry=True,
                                             content=f'an error occured, {e}', allowed_mentions={"parse": []})
                    response = webhook.execute()
