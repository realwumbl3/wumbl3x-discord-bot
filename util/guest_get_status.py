import requests
import logging
import json

GUEST_BEARER = "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"


class GuestToken:
    def __init__(self, VERBOSE=False):
        self.token = None
        self.VERBOSE = VERBOSE

    def get(self):
        if not self.token:
            self.fresh_token()
        return self.token

    def fresh_token(self):
        r = requests.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={"Authorization": GUEST_BEARER},
        )
        self.token = json.loads(r.text)["guest_token"]
        self.VERBOSE and logging.info(f"twitter API guestToken: {self.token }")


XGuestToken = GuestToken()


def guest_get_status(tweet_id):
    tweet = requests.get(
        f"https://api.twitter.com/1.1/statuses/show/{tweet_id}.json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1",
        headers={"Authorization": GUEST_BEARER, "x-guest-token": XGuestToken.get()},
    )
    output = tweet.json()
    if "errors" in output:
        error = output["errors"][0]
        raise Exception(error["code"], error["message"])
    return output


print(guest_get_status("1638368320545255424"))
