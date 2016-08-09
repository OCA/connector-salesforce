# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from ..unit.binder import SalesforceBinder


class SalesforceAccount(models.Model):
    _inherit = 'salesforce.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _name = 'connector.salesforce.account'
    _description = 'Import SF Account into res.partner model'

    sf_shipping_partner_id = fields.Many2one(
        'res.partner',
        'Salesforce shipping partner'
    )

    openerp_id = fields.Many2one('res.partner',
                                 string='Partner',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('sf_id_uniq', 'unique(backend_id, salesforce_id)',
         'A Partner with same Salesforce id already exists.')
    ]

SalesforceBinder._model_name.append('connector.salesforce.account')
