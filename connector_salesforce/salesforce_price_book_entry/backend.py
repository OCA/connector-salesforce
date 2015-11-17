# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2015 Camptocamp SA
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
from openerp import models, fields, api


class SalesforcePriceBookEntryBackend(models.Model):

    _inherit = 'connector.salesforce.backend'

    sf_last_entry_import_sync_date = fields.Datetime(
        'Last Entry Import Date'
    )
    sf_entry_mapping_ids = fields.One2many(
        comodel_name='connector.salesforce.pricebook.entry.mapping',
        inverse_name='backend_id',
        string='Price Book Entries mapping'
    )

    @api.multi
    def import_sf_entry(self):
        """Run the import of Salesforce pricebook entries for given backend"""
        self._import(
            'connector.salesforce.pricebook.entry',
            'direct',
            'sf_last_entry_import_sync_date',
        )

    @api.multi
    def import_sf_entry_delay(self):
        """Run the import of Salesforce pricebook entries for given backend
        using jobs"""
        self._import(
            'connector.salesforce.pricebook.entry',
            'delay',
            'sf_last_entry_import_sync_date',
        )


class SalesforcePriceBoookEntryMapping(models.Model):
    """Configuration between currency and pricelist version"""

    _name = 'connector.salesforce.pricebook.entry.mapping'

    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
    )
    pricelist_version_id = fields.Many2one(
        'product.pricelist.version',
        'Price list version',
        required=True,
    )
    backend_id = fields.Many2one(
        'connector.salesforce.backend',
        'Salesforce Backend',
        required=True,
    )
