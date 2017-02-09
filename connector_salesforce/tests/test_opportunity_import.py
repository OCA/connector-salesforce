# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import MagicMock
from .common import CommonTest, mock_simple_salesforce
from . import fixture


class OpportunityImportTest(CommonTest):

    def setUp(self):
        """Setup test using erp as product master"""
        super(OpportunityImportTest, self).setUp()
        self.model_name = 'connector.salesforce.opportunity'
        self.imported_model = self.registry(self.model_name)
        self.conn_env = self.get_connector_env(self.model_name)
        prod_id = self.registry('connector.salesforce.product').create(
            self.cr,
            self.uid,
            {
                'salesforce_id': 'uuid_product_01',
                'name': 'Product exported on SF',
                'sale_ok': True,
                'list_price': 0.0,
                'backend_id': self.backend.id,
            }
        )
        self.product = self.registry('connector.salesforce.product').browse(
            self.cr,
            self.uid,
            prod_id
        )

    def test_simple_import(self):
        pl_version = self.get_euro_pricelist_version()
        self.registry('connector.salesforce.pricebook.entry.mapping').create(
            self.cr,
            self.uid,
            {
                'backend_id': self.backend.id,
                'currency_id': pl_version.pricelist_id.currency_id.id,
                'pricelist_version_id': pl_version.id,
            }
        )
        response = MagicMock(name='simple_quotation_import')
        response.side_effect = [
            {'records': [{'Id': 'uuid_opportunity_01'}]},
            {'records': [{'Id': 'uuid_opportunity_01'}]},
            {'records': [{'dummy': 'dummy'}]},
            fixture.opportunity,
            {'records': [{'dummy': 'dummy'}]},
            fixture.account,
            {'records': [{'Id': 'uuid_opportunityline_01'}]},
            {'records': [{'dummy': 'dummy'}]},
            fixture.opportunity_line,
            {
                'records': [
                    {'PricebookEntry': {'Product2Id': 'uuid_product_01'}}
                ]
            },
        ]
        with mock_simple_salesforce(response):
            self.backend.import_sf_opportunity()
        imported_id = self.imported_model.search(
            self.cr,
            self.uid,
            [('salesforce_id', '=', 'uuid_opportunity_01'),
             ('backend_id', '=', self.backend.id)]
        )
        self.assertTrue(imported_id)
        self.assertEqual(len(imported_id), 1)
        imported = self.imported_model.browse(
            self.cr,
            self.uid,
            imported_id[0]
        )
        self.assertEqual(imported.origin, 'A won opportunity')
        self.assertEqual(imported.order_policy, 'manual')
        self.assertEqual(imported.currency_id.name, 'EUR')
        self.assertEqual(imported.section_id.id, 1)
        self.assertEqual(imported.partner_id.name, 'Main name')
        self.assertEqual(imported.partner_invoice_id.name, 'Main name')
        self.assertEqual(imported.partner_shipping_id.name, 'Main name')
        self.assertEqual(imported.partner_id, imported.partner_invoice_id)
        self.assertNotEqual(imported.partner_id, imported.partner_shipping_id)
        self.assertEqual(imported.state, 'draft')
        self.assertEqual(imported.pricelist_id.currency_id.name, 'EUR')
        self.assertEqual(imported.amount_total, 160.0)
        self.assertEqual(len(imported.order_line), 1)

        order_line = imported.order_line[0]
        self.assertEqual(order_line.product_id, self.product.openerp_id)
        self.assertEqual(order_line.product_uos_qty, 2.0)
        self.assertEqual(order_line.price_unit, 100.0)
        self.assertEqual(order_line.product_uom_qty, 2.0)
        self.assertEqual(order_line.price_subtotal, 160.0)
        self.assertEqual(order_line.discount, 20.0)
        self.assertEqual(order_line.name, 'A sale')
        self.assertEqual(order_line.state, 'draft'),
