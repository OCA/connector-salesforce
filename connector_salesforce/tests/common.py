# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import nested, contextmanager
from mock import patch, MagicMock

import openerp.tests.common as test_common

SF_SPECS = ['query_all', 'delete', 'get', 'updated',
            'deleted', 'update', 'create', 'upsert']


class CommonTest(test_common.TransactionCase):

    def _get_backend(self):
        """Provide a fixture backend record for the test"""
        backend_model = self.env['connector.salesforce.backend']
        backend = backend_model.search(
            [('name', '=', 'Salesforce Backend Test')]
        )
        if backend:
            return backend[0]
        else:
            backend = backend_model.create(
                {'name': 'Salesforce Backend Test',
                 'version': '15',
                 'url': 'Dummy',
                 'authentication_method': 'oauth2',
                 'consumer_secret': 'Dummy',
                 'callback_url': 'httpd://dummy.dummy',
                 'consumer_code': 'Dummy',
                 'consumer_token': 'Dummy',
                 'consumer_key': 'Dummy',
                 'sf_sales_team_id': 1,
                 'consumer_refresh_token': 'Dummy'}
            )
        return backend

    def get_connector_env(self, model_name):
        self.assertTrue(self.backend)
        return self.backend.get_connector_environment(model_name)

    def setUp(self):
        super(CommonTest, self).setUp()
        self.backend = self._get_backend()

    def get_euro_pricelist_version(self):
        pl_version = self.env['product.pricelist.version'].search(
            [('pricelist_id.currency_id.name', '=', 'EUR'),
             ('pricelist_id.type', '=', 'sale')]
        )
        self.assertTrue(pl_version)
        return pl_version


@contextmanager
def mock_simple_salesforce(response_mock):
    """Context manager that will mock the request object used
    to talk with Salesforce

    :param response_mock: A response mock that will be used as
                          the result of a Salesforce interogation
    :type response_mock: :py:class:`mock.MagicMock`

    :yield: current execution stack
    """

    def _get_response(*args, **kwargs):
        return response_mock

    for fun in SF_SPECS:
        setattr(response_mock, fun, response_mock)
    klass = ('openerp.addons.connector_salesforce.unit'
             '.rest_api_adapter.SalesforceRestAdapter')
    connection_to_patch = "%s.%s" % (klass, 'get_sf_connection')
    type_to_patch = "%s.%s" % (klass, 'get_sf_type')
    return_mock = MagicMock()
    return_mock.side_effect = _get_response
    with nested(patch(connection_to_patch, return_mock),
                patch(type_to_patch, return_mock)):
        yield
