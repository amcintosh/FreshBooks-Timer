from requests_oauthlib import OAuth2Session
import logging
from fbtimer.service.config import write_token

log = logging.getLogger(__name__)

CLIENT_ID = '503203a5111a38c1af565068dcaca80f56ca1c6983c6ed7c39d374bc67d42179'
CLIENT_SECRET = '24c720272db55588895944729d562ca5baff2e1ced7039724dfeb5500fc311fa'


FRESHBOOKS_BASE_URL = 'https://api.freshbooks.com/'
FRESHBOOKS_TOKEN_URL = 'auth/oauth/token'


def make_req(token, url):
    extra = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    client = OAuth2Session(
        CLIENT_ID,
        token=token,
        auto_refresh_url='{}{}'.format(FRESHBOOKS_BASE_URL, FRESHBOOKS_TOKEN_URL),
        auto_refresh_kwargs=extra,
        token_updater=write_token
    )
    client.headers.update(fb_headers())
    res = client.get('{}{}'.format(FRESHBOOKS_BASE_URL, url))
    return res


def authorize():
    redirect_uri = 'https://github.com/amcintosh/FreshBooks-Timer'
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(
        'https://my.freshbooks.com/service/auth/oauth/authorize')

    print('Please go to %s and authorize access.' % authorization_url)

    authorization_response = input('Enter the full callback URL: ')

    oauth.headers.update(fb_headers())
    token = oauth.fetch_token(
        token_url='{}{}'.format(FRESHBOOKS_BASE_URL, FRESHBOOKS_TOKEN_URL),
        authorization_response=authorization_response,
        client_secret=CLIENT_SECRET,
        token=state
    )
    write_token(token)
    return token


def fb_headers():
    return {
        "Api-Version": "alpha",
        "Content-Type": "application/json"
    }
