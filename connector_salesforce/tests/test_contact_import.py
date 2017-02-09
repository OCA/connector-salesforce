# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import MagicMock
from .common import CommonTest, mock_simple_salesforce
from . import fixture


class ContactImportTest(CommonTest):

    def setUp(self):
        super(ContactImportTest, self).setUp()
        self.model_name = 'connector.salesforce.contact'
        self.imported_model = self.env[self.model_name]
        self.conn_env = self.get_connector_env(self.model_name)

    def test_simple_import(self):
        pl_version = self.get_euro_pricelist_version()
        self.env['connector.salesforce.pricebook.entry.mapping'].create(
            {
                'backend_id': self.backend.id,
                'currency_id': pl_version.pricelist_id.currency_id.id,
                'pricelist_version_id': pl_version.id,
            }
        )
        response = MagicMock(name='simple_contact_import')
        response.side_effect = [

            {'records': [{'Id': 'uuid_contact_01'}]},
            {'records': [{'dummy': 'dummy'}]},
            fixture.contact,
            {'records': [{'dummy': 'dummy'}]},
            fixture.account,
        ]
        with mock_simple_salesforce(response):
            self.backend.import_sf_contact()

        imported = self.imported_model.search(
            [('salesforce_id', '=', 'uuid_contact_01'),
             ('backend_id', '=', self.backend.id)]
        )
        self.assertTrue(imported)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported.name, 'Contact lastname Contact firstname')
        self.assertEqual(imported.street, 'Contact street')
        self.assertEqual(imported.city, 'Contact city')
        self.assertEqual(imported.fax, '+41 21 619 10 10')
        self.assertEqual(imported.phone, '+41 21 619 10 12')
        self.assertEqual(imported.sf_assistant_phone, '+41 21 619 10 15')
        self.assertEqual(imported.sf_other_phone, '+41 21 619 10 13')
        self.assertEqual(imported.mobile, '+41 21 619 10 14')
        self.assertEqual(imported.phone, '+41 21 619 10 12')
        self.assertEqual(imported.email, 'contact@mail.ch')
        self.assertEqual(imported.zip, 'Contact zip')
        self.assertEqual(imported.state_id.name, 'Contact state')
        self.assertEqual(imported.country_id.code, 'CH')
        self.assertFalse(imported.is_company)
        self.assertEqual(imported.parent_id.name, 'Main name')
