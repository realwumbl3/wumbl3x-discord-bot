import requests
import re


class Twitter:
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

    def search(self, query):
        # query actual data
        param = {
            "include_profile_interstitial_type": "1",
            "include_blocking": "1",
            "include_blocked_by": "1",
            "include_followed_by": "1",
            "include_want_retweets": "1",
            "include_mute_edge": "1",
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
            "simple_quoted_tweet": "true",
            "q": query,
            "count": "100",
            "query_source": "typed_query",
            "pc": "1",
            "spelling_corrections": "1",
            "ext": "mediaStats,highlightedLabel",
        }

        res = self.s.get(
            url="https://twitter.com/i/api/2/search/adaptive.json",
            params=param,
        )
        if res.status_code == 200:
            return res.json()["globalObjects"]["tweets"]
        else:
            return []


from pprint import pprint

if __name__ == "__main__":
    # same query as on the website
    # -> can be created via advanced search
    q = "(#タガタメ資料館) (from:FgG_tagatame OR from:GrowArtistry) until:2020-02-1 since:2016-01-1 -filter:replies"
    # init class
    t = Twitter()
    # do the actual query
    tweets = t.search(q)
    pprint(tweets)
