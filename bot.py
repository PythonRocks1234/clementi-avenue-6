import tweepy
from tweepy import OAuthHandler, Stream, StreamingClient
import json

from discord_webhook import DiscordWebhook, DiscordEmbed

username = "@LTAtrafficnews"
userId = 4291685673

class TweetListener(StreamingClient):
    """ A listener handles tweets that are received in real time.  """

    def on_data(self, status):
        try:
            data = json.loads(status)['data']
            tweet_id = data['id']
            text = data['text']
            contains = ("Clementi Ave 6" in text) or ("Clementi Avenue 6" in text)
            # if rate_limit_retry is True then in the event that you are being rate 
            # limited by Discord your webhook will automatically be sent once the 
            # rate limit has been lifted
            webhook = DiscordWebhook(url='https://discord.com/api/webhooks/URL', rate_limit_retry=True)
            embed = DiscordEmbed(
                title="New Post", color=('00ff00' if contains else 'ff0000')
            )
            embed.set_timestamp()
            embed.add_embed_field(name="User", value=username, inline=False)
            embed.add_embed_field(name="Tweet ID", value=f'@{tweet_id}', inline=False)
            embed.add_embed_field(name="Text", value=text, inline=False)
            embed.add_embed_field(name="Clementi Avenue 6", value=str(contains), inline=False)
            
            webhook.add_embed(embed)
            response = webhook.execute()
        except Exception as e:
            webhook = DiscordWebhook(url='https://discord.com/api/webhooks/URL', rate_limit_retry=True,
                                     content=f'an error occured, {e}', allowed_mentions={"parse": []})
            response = webhook.execute()
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False
        print(status_code)

if __name__ == '__main__':
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/URL', rate_limit_retry=True,
                            content=f'bot started listening to {username}', allowed_mentions={"parse": []})
    response = webhook.execute()
    listen = TweetListener("TOKEN")
    listen.add_rules(tweepy.StreamRule(f"from:{userId}"))
    listen.filter()
