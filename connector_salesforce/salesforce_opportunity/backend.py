# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SalesforceOpportunityBackend(models.Model):

    _inherit = 'connector.salesforce.backend'

    sf_last_opportunity_import_sync_date = fields.Datetime(
        'Last Opportunity Import Date'
    )

    sf_sales_team_id = fields.Many2one(
        'crm.case.section',
        'Sales team to be used',
        required=True,
    )

    @api.multi
    def import_sf_opportunity(self):
        """Run the import of Salesforce opportunites for given backend"""
        self._import(
            'connector.salesforce.opportunity',
            'direct',
            'sf_last_opportunity_import_sync_date',
        )

    @api.multi
    def import_sf_opportunity_delay(self):
        """Run the import of Salesforce opportunites for given backend
        using jobs
        """
        self._import(
            'connector.salesforce.opportunity',
            'delay',
            'sf_last_opportunity_import_sync_date',
        )
