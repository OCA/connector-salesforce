# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SalesforceAccountBackend(models.Model):

    _inherit = 'connector.salesforce.backend'

    sf_last_account_import_sync_date = fields.Datetime(
        'Last Account Import Date'
    )

    @api.multi
    def import_sf_account(self):
        """Run the import of Salesforce account for given backend"""
        self._import(
            'connector.salesforce.account',
            'direct',
            'sf_last_account_import_sync_date',
        )

    @api.multi
    def import_sf_account_delay(self):
        """Run the import of Salesforce account for given backend using jobs"""
        self._import(
            'connector.salesforce.account',
            'delay',
            'sf_last_account_import_sync_date',
        )
