# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
from urllib import quote, urlencode
from urlparse import parse_qs, urljoin
import simplejson as json


class SalesforceOauth2MAnager(object):
    """Utility class to manage Salesforce
    Oauth2 connexion
    """
    def __init__(self, backend_record):
        """Constructor taht set main url and
        properties.
        """
        self.backend = backend_record
        self.base_login_url = 'https://login.salesforce.com/'
        self.authorization_url = "services/oauth2/authorize"
        self.token_url = "services/oauth2/token"
        self.redirect_uri = urljoin(self.backend.callback_url,
                                    "salesforce/oauth")
        if self.backend.sandbox:
            self.base_login_url = "https://test.salesforce.com/"

    def authorize_url(self, scope='', **kwargs):
        """
        Returns the callback url to redirect the user after authorization
        :param scope: Oauth2 scope see
        https://help.salesforce.com/HTViewHelpDoc?id=remoteaccess_oauth_scopes.htm&language=en_US
        :type scope: str
        :return: authorize URL of Odoo must be HTTPS URL
        """

        oauth_params = {
            'redirect_uri': self.redirect_uri,
            'client_id': self.backend.consumer_key,
            'scope': scope
        }
        oauth_params.update(kwargs)
        return "%s%s?%s" % (
            self.base_login_url,
            quote(self.authorization_url),
            urlencode(oauth_params)
        )

    def get_token(self, **kwargs):
        """
        Requests an access token variatic keyword arguments
        will be added to POST request data
        :return: session token
        :rtype: str
        """
        url = "%s%s" % (self.base_login_url, quote(self.token_url))
        data = {'code': self.backend.consumer_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'client_id': self.backend.consumer_key,
                'client_secret': self.backend.consumer_secret}
        data.update(kwargs)
        response = requests.post(url, data=data)

        if isinstance(response.content, basestring):
            try:
                content = json.loads(response.content)
            except ValueError:
                content = parse_qs(response.content)
        else:
            content = response.content
        return content

    def refresh_token(self, **kwargs):
        """
        Requests an refresh acces token. It is used to obtain
        new token when session expire.
        Variatic keyword arguments will be added to POST request data

        :return: session token
        :rtype: str
        """
        url = "%s%s" % (self.base_login_url, quote(self.token_url))
        data = {'refresh_token': self.backend.consumer_refresh_token,
                'client_id': self.backend.consumer_key,
                'client_secret': self.backend.consumer_secret,
                'grant_type': 'refresh_token'}
        data.update(kwargs)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=data, headers=headers)
        if isinstance(response.content, basestring):
            try:
                content = json.loads(response.content)
            except ValueError:
                content = parse_qs(response.content)
        else:
            content = response.content
        return content
