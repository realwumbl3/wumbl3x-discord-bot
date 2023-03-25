import requests
import json

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1086833065600503829/jX5gFNirJEL6kwsM9FcYJbGFy38ATHS0pTf-kZgbji9fFo6aiQg4aLSbp0p17yXjNlg-"

res = requests.post(
    DISCORD_WEBHOOK_URL,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://discord.wumbl3.xyz, 1.0)",
    },
    data=json.dumps(
        {
            "content": "new tweet!",
            "embeds": [
                {
                    "url": "https://twitter.com/i/status/1637279056897925122",
                    "image": {"url": "https://pbs.twimg.com/media/FrjInmhWYAITn0j.jpg"},
                    "title": "New liked tweet!\ntwitter..Reptilligator...1637279056897925122",
                    "color": 16063743,
                    "timestamp": "2023-03-19T02:25:20.000Z",
                    "author": {
                        "name": "By @Reptilligator",
                        "url": "https://twitter.com/Reptilligator",
                        "icon_url": "https://pbs.twimg.com/profile_images/585581014543704064/agW8mO3w_400x400.png",
                    },
                    "footer": {
                        "text": "twitter",
                        "icon_url": "https://discord.wumbl3.xyz/assets/yellow.png",
                    },
                },
                {
                    "url": "https://twitter.com/i/status/1637279056897925122",
                    "image": {"url": "https://pbs.twimg.com/media/FrjIn73WIAA3uLw.jpg"},
                },
            ],
        }
    ),
)

print(res.json())
