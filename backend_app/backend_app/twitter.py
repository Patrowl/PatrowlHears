from django.conf import settings
import twitter

if settings.TWITTER_ENABLED is True:
    twitter_api = twitter.Api(
        consumer_key=settings.TWITTER_CONSUMER_KEY,
        consumer_secret=settings.TWITTER_CONSUMER_SECRET,
        access_token_key=settings.TWITTER_ACCESS_TOKEN_KEY,
        access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
    )

    twitter_api.SetUserAgent("PatrowlHears Feeder")
else:
    twitter_api = None
