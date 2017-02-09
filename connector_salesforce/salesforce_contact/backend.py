# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SalesforceContactBackend(models.Model):

    _inherit = 'connector.salesforce.backend'

    sf_last_contact_import_sync_date = fields.Datetime(
        'Last Contact Import Date'
    )

    @api.multi
    def import_sf_contact(self):
        """Run the import of Salesforce contacts for given backend"""
        self._import(
            'connector.salesforce.contact',
            'direct',
            'sf_last_contact_import_sync_date',
        )

    @api.multi
    def import_sf_contact_delay(self):
        """Run the import of Salesforce contacts for given backend
        using jobs
        """
        self._import(
            'connector.salesforce.contact',
            'delay',
            'sf_last_contact_import_sync_date',
        )
