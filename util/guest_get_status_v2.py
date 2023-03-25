import requests
import re


class v2GuestTwitter:
    def __init__(self):
        self.s = requests.Session()
        self.get_tokens()

    def get_tokens(self):
        s = self.s
        s.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
                "accept": "*/*",
                "accept-language": "de,en-US;q=0.7,en;q=0.3",
                "accept-encoding": "gzip, deflate, utf-8",
                "te": "trailers",
            }
        )

        # get guest_id cookie
        r = s.get("https://twitter.com")

        # get auth token
        main_js = s.get(
            "https://abs.twimg.com/responsive-web/client-web/main.e46e1035.js",
        ).text
        token = re.search(r"s=\"([\w\%]{104})\"", main_js)[1]
        s.headers.update({"authorization": f"Bearer {token}"})

        # activate token and get guest token
        guest_token = s.post("https://api.twitter.com/1.1/guest/activate.json").json()[
            "guest_token"
        ]
        s.headers.update({"x-guest-token": guest_token})

    def get_conversation(self, tweet_id):
        param = {
            "include_profile_interstitial_type": "1",
            "include_can_dm": "1",
            "include_can_media_tag": "1",
            "skip_status": "1",
            "cards_platform": "Web-12",
            "include_cards": "1",
            "include_ext_alt_text": "true",
            "include_quote_count": "true",
            "include_reply_count": "1",
            "tweet_mode": "extended",
            "include_entities": "true",
            "include_user_entities": "true",
            "include_ext_media_color": "true",
            "include_ext_media_availability": "true",
            "send_error_codes": "true",
            "include_tweet_replies": "false",
            "tweet_id": tweet_id,
        }
        res = self.s.get(
            url=f"https://api.twitter.com/2/timeline/conversation/{tweet_id}.json",
            params=param,
        )
        return return_tweets(res)


def return_tweets(res):
    if res.status_code == 200:
        return res.json()["globalObjects"]["tweets"]
    else:
        return []


guest_twitter = v2GuestTwitter()


from pprint import pprint

pprint(guest_twitter.get_status("1636479985438302209"))
