# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import MagicMock
from .common import CommonTest, mock_simple_salesforce
from . import fixture


class PriceBookImportTest(CommonTest):

    def setUp(self):
        """Setup test using erp export by default"""
        super(PriceBookImportTest, self).setUp()
        self.model_name = 'connector.salesforce.pricebook.entry'
        self.imported_model = self.env[self.model_name]
        self.conn_env = self.get_connector_env(self.model_name)
        self.product = self.env['connector.salesforce.product'].create(
            {
                'salesforce_id': 'uuid_product_01',
                'name': 'Product exported on SF',
                'sale_ok': True,
                'list_price': 0.0,
                'backend_id': self.backend.id,
            }
        )

    def test_simple_import(self):
        pl_version = self.get_euro_pricelist_version()
        self.env['connector.salesforce.pricebook.entry.mapping'].create(
            {
                'backend_id': self.backend.id,
                'currency_id': pl_version.pricelist_id.currency_id.id,
                'pricelist_version_id': pl_version.id,
            }
        )
        response = MagicMock(name='simple_pricebookentry_import')
        response.side_effect = [
            {'records': [{'Id': 'uuid_pricebookentry_01'}]},
            {'records': [{'dummy': 'dummy'}]},
            fixture.price_book_entry,
        ]
        with mock_simple_salesforce(response):
            self.backend.import_sf_entry()
        imported = self.imported_model.search(
            [('salesforce_id', '=', 'uuid_pricebookentry_01'),
             ('backend_id', '=', self.backend.id)]
        )
        self.assertTrue(imported)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported.price_version_id, pl_version)
        self.assertEqual(imported.price_surcharge, 200.00)
        self.assertEqual(imported.product_id, self.product.openerp_id)
