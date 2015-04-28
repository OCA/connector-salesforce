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
from openerp import models, fields, api


class SalesforceProductBackend(models.Model):

    _inherit = 'connector.salesforce.backend'

    sf_last_product_import_sync_date = fields.Datetime(
        'Last Product Import Date'
    )

    sf_last_product_export_sync_date = fields.Datetime(
        'Last Product Export Date'
    )

    sf_product_master = fields.Selection(
        [('sf', 'Salesforce'), ('erp', 'OpenERP/Odoo')],
        string='Select Master For Product',
        help='Select the master for the products. '
             'Bidirectional/Conflicts are not managed so once set '
             'you should not modify direction',
        required=True,
        default='erp',
    )
    sf_product_type_mapping_ids = fields.One2many(
        comodel_name='connector.salesforce.product.type.mapping',
        inverse_name='backend_id',
        string='Product Type to SF Family Mapping'
    )

    @api.multi
    def import_sf_product(self):
        """Run the import of Salesforce products for given backend"""
        self._import(
            'connector.salesforce.product',
            'direct',
            'sf_last_product_import_sync_date',
        )
        return True

    @api.multi
    def import_sf_product_delay(self):
        """Run the import of Salesforce products for given backend
        using jobs"""
        self._import(
            'connector.salesforce.product',
            'delay',
            'sf_last_product_import_sync_date',
        )
        return True

    @api.multi
    def export_sf_product(self):
        """Run the export of Salesforce products for given backend"""
        self._export(
            'connector.salesforce.product',
            'direct',
            'sf_last_product_export_sync_date',
        )
        return True

    @api.multi
    def export_sf_product_delay(self):
        """Run the import of Salesforce products for given backend
        using jobs"""
        self._export(
            'connector.salesforce.product',
            'delay',
            'sf_last_product_export_sync_date',
        )
        return True


class SalesforceProductTypeMApping(models.Model):

    _name = 'connector.salesforce.product.type.mapping'

    @api.model
    def _get_product_types(self):
        return self.env['product.template']._fields['type'].selection

    product_type = fields.Selection(
        _get_product_types,
        'Odoo/OpenERP product type',
        required=True,
    )
    sf_family = fields.Char(
        'Sales Force Product Family',
        required=True,
    )
    backend_id = fields.Many2one(
        'connector.salesforce.backend',
        'Salesforce Backend',
        required=True,
    )
