# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from __future__ import absolute_import
import simplejson
from ..lib.oauth2_utils import SalesforceOauth2MAnager
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
from openerp.addons.connector import session as csession, connector
from ..unit.importer_synchronizer import batch_import, delayed_batch_import
from ..unit.exporter_synchronizer import batch_export, delayed_batch_export


class SalesforceBackend(models.Model):
    """Salesforce backend

    Please refer to connector backend documentation

    There are 2 supported ways to access a Salesforce instance
    Oauth2 flow
    -----------
    In order to use it you have to add a remote application in Salesforce
    and enable Oauth login.

    The created remote access app must have following parameters:

    Permitted Users -->	All users may self-authorize
    Callback URL --> public_odoo_url/salesforce/oauth


    Once done you have to manage your app and ensure the
    `Refresh token is valid until revoked` parameter is set.

    The following authentication method is still exprimental

    User Password flow
    ------------------
    This flow allows a user to connect to api using SOAP access
    in order to get a token. This approach is simpler but less secure
    The first step is to pass the domain of your Salesforce instance
    and an access token straight in Odoo backend.

    You must have the full URL e.g (https://na1.salesforce.com)
    of your instance.

    There are also two means of authentication:
    - Using username, password and security token
    - Using IP filtering, username, password and organizationId
    """

    _name = "connector.salesforce.backend"
    _inherit = "connector.backend"
    _description = """Salesforce Backend"""
    _backend_type = "salesforce"

    @api.model
    def _select_versions(self):
        """ Available versions

        Can be inherited to add custom versions.

        :return: list of tuple of available versions
        :rtype: list
        """
        return self._select_versions_hook()

    @api.model
    def _select_versions_hook(self):
        """ Available versions

        Can be inherited to add custom versions.

        :return: list of tuple of available versions
        :rtype: list
        """
        return [('15', "Winter'15")]

    authentication_method = fields.Selection(
        [
            ('pwd_token', 'Based on User, Password, Token'),
            ('oauth2', 'OAuth 2'),
            ('ip_filtering', 'Based on IP Filter and OrganizationId')
        ],
        string='Authentication Method',
        default='oauth2',
    )

    name = fields.Char(
        'Name',
        required=True
    )

    version = fields.Selection(
        selection='_select_versions',
        string='Version',
        required=True
    )

    url = fields.Char(
        'URL',
        required=True,
    )

    username = fields.Char(
        'User Name',
    )

    password = fields.Char(
        'Password',
    )

    consumer_key = fields.Char(
        'OAuth2 Consumer Key',
    )

    consumer_secret = fields.Char(
        'OAuth2 secret',
    )

    consumer_code = fields.Char(
        'OAuth2 client authorization code'
    )
    consumer_refresh_token = fields.Char(
        'OAuth2 Refresh Token'
    )
    consumer_token = fields.Char(
        'OAuth2 Token'
    )
    callback_url = fields.Char(
        'Public secure URL of Odoo (HTTPS)',
    )
    security_token = fields.Char(
        'Password flow Security API token',
    )

    organization_uuid = fields.Char('OrganizationId')

    sandbox = fields.Boolean(
        'Connect on sandbox instance',
    )

    @api.model
    def _enforce_param(self, param_name):
        """Ensure configuration parameter is set on backend record

        :param param_name: name of parameter to validate
        :type param_name: str

        :return: True if parameter is set or raise an exception
        :rtype: bool
        """
        self.ensure_one()
        if not getattr(self, param_name, None):
            f_model = self.env['ir.model.fields']
            field = f_model.search(
                [('model', '=', self._name),
                 ('name', '=', param_name)],
            )
            if len(field) == 1:
                field_name = field.field_description
            else:
                field_name = param_name
            raise exceptions.Warning(
                _('Configuration %s is mandatory with '
                  'current authentication method') % field_name
            )
        return True

    def _enforce_url(self):
        """Predicate hook to see if URL must be enforced
        when validating configuration"""
        return True

    @api.multi
    def _validate_configuration(self):
        """Ensure configuration on backend record is correct

        We also test required parameters in order to
        support eventual server env based configuration
        """
        for config in self:
            if self._enforce_url():
                config._enforce_param('url')
            if config.authentication_method == 'ip_filtering':
                config._enforce_param('organization_uuid')
                config._enforce_param('username')
                config._enforce_param('password')
            if config.authentication_method == 'pwd_token':
                config._enforce_param('security_token')
                config._enforce_param('username')
                config._enforce_param('password')
            if config.authentication_method == 'oauth2':
                config._enforce_param('consumer_key')
                config._enforce_param('consumer_secret')
                config._enforce_param('callback_url')
        return True

    _constraints = [
        (_validate_configuration, 'Configuration is invalid', [])
    ]

    @api.model
    def get_connector_environment(self, model_name):
        """Returns a connector environment related to model and current backend

        :param model_name: Odoo model name taken form `_name` property
        :type model_name: str

        :return: a connector environment related to model and current backend
        :rtype: :py:class:``connector.ConnectorEnvironment``

        """
        session = csession.ConnectorSession(
            self.env.cr,
            self.env.uid,
            self.env.context
        )
        env = connector.ConnectorEnvironment(self, session, model_name)
        return env

    @api.model
    def _get_oauth2_handler(self):
        """Initialize and return an instance of Salesforce OAuth2 Helper

        :return: An OAuth2 helper instance
        :rtype: :py:class:`..lib.oauth2_utils.SalesforceOauth2MAnager`
        """
        self.ensure_one()
        oauth2_handler = SalesforceOauth2MAnager(
            self
        )
        return oauth2_handler

    @api.multi
    def redirect_to_validation_url(self):
        """Retrieve Oauth2 authorization URL"""
        self.ensure_one()
        oauth2_handler = self._get_oauth2_handler()
        auth_url = oauth2_handler.authorize_url(
            response_type='code',
            state=simplejson.dumps(
                {'backend_id': self.id, 'dbname': self.env.cr.dbname}
            )
        )
        return {
            'name': 'Authorize Odoo/OpenERP',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': auth_url
        }

    @api.multi
    def get_token(self):
        """Refresh current backend Oauth2 token
        using the Salesforce refresh token
        """
        self.ensure_one()
        self._get_token(refresh=True)
        return {}

    @api.multi
    def refresh_token(self):
        """Refresh current backend Oauth2 token
        using the Salesforce refresh token
        """
        self.ensure_one()
        self._get_token(refresh=True)
        return {}

    @api.model
    def _get_token(self, refresh=False):
        """Obtain current backend Oauth2 token and or refresh Token"""
        oauth2_handler = self._get_oauth2_handler()
        if refresh:
            if not self.consumer_refresh_token:
                raise ValueError(
                    'Trying to refresh token but no saved refresh token'
                )
            response = oauth2_handler.refresh_token()
        else:
            response = oauth2_handler.get_token()
        if response.get('error'):
            raise Exception(
                'Can not get Token: %s %s' % (
                    response['error'],
                    response['error_description']
                )
            )
        # refresh token must absolutly be saved else
        # all authorization process must be redone
        token_vals = {'consumer_token': response['access_token']}
        if response.get('refresh_token'):
            token_vals['consumer_refresh_token'] = response['refresh_token']
        self.write(token_vals)
        return response

    @api.model
    def _import(self, model, mode, date_field, full=False):
        """Run an import for given backend and model

        :param model: The Odoo binding model name found in _name
        :type model: str
        :param mode: import mode must be in  `('direct', 'delay')`
                     if mode is delay import will be done using jobs
        :type mode: str

        :param date_field: name of the current backend column that store
                           the last import date for current import

        :return: import start time
        :rtype: str
        """
        assert mode in ('direct', 'delay'), "Invalid mode"
        import_start_time = fields.Datetime.now()
        session = csession.ConnectorSession(
            self.env.cr,
            self.env.uid,
            self.env.context
        )
        date = getattr(self, date_field, False) if full is False else False
        if mode == 'direct':
            batch_import(
                session,
                model,
                self.id,
                date=date
            )
        else:
            delayed_batch_import(
                session,
                model,
                self.id,
            )
        self.write({date_field: import_start_time})
        return import_start_time

    @api.model
    def _export(self, model, mode, date_field, full=False):
        """Run an export for given backend and model

        :param model: The Odoo binding model name found in _name
        :type model: str
        :param mode: export mode must be in  `('direct', 'delay')`
                     if mode is delay export will be done using jobs
        :type mode: str

        :param date_field: name of the current backend column that store
                           the last export date for current export

        :return: export start time
        :rtype: str
        """
        assert mode in ['direct', 'delay'], "Invalid mode"
        session = csession.ConnectorSession(
            self.env.cr,
            self.env.uid,
            self.env.context
        )
        export_start_time = fields.Datetime.now()
        date = getattr(self, date_field, False) if full is False else False
        if mode == 'direct':
            batch_export(
                session,
                model,
                self.id,
                date=date,
            )
        else:
            delayed_batch_export(
                session,
                model,
                self.id,
                date=date
            )
        self.write({date_field: export_start_time})
        return export_start_time


class SalesforceBindingModel(models.AbstractModel):

    _name = 'salesforce.binding'
    _inherit = 'external.binding'

    backend_id = fields.Many2one(
        'connector.salesforce.backend',
        'salesforce Backend',
        required=True,
        ondelete='restrict'
    )
    salesforce_id = fields.Char('Salesforce ID')
    salesforce_sync_date = fields.Datetime('Salesforce Synchro. Date')
