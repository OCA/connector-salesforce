# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from ..unit.binder import SalesforceBinder


class SalesforceContact(models.Model):
    _inherit = 'salesforce.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _name = 'connector.salesforce.contact'
    _description = 'Import SF Contact into res.partner model'

    openerp_id = fields.Many2one('res.partner',
                                 string='Partner',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('sf_id_uniq', 'unique(backend_id, salesforce_id)',
         'A partner with same Salesforce id already exists')
    ]

SalesforceBinder._model_name.append('connector.salesforce.contact')


class SalesforceResPartner(models.Model):
    _inherit = 'res.partner'

    sf_assistant_phone = fields.Char('Assistant Phone')
    sf_other_phone = fields.Char('Other Phone')
