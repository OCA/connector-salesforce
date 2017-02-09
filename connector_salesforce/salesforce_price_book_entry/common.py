# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from ..unit.binder import SalesforceBinder


class SalesforcePriceBookEntry(models.Model):
    _inherit = 'salesforce.binding'
    _inherits = {'product.pricelist.item': 'openerp_id'}
    _name = 'connector.salesforce.pricebook.entry'
    _description = 'Import SF Price Book entry into product.pricelist.item'

    openerp_id = fields.Many2one('product.pricelist.item',
                                 string='Price Item',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('sf_id_uniq', 'unique(backend_id, salesforce_id)',
         'A parnter with same Salesforce id already exists')
    ]

SalesforceBinder._model_name.append('connector.salesforce.pricebook.entry')
