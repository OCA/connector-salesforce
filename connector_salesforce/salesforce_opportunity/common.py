# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from ..unit.binder import SalesforceBinder


class SalesforceOpportunity(models.Model):
    _inherit = 'salesforce.binding'
    _inherits = {'sale.order': 'openerp_id'}
    _name = 'connector.salesforce.opportunity'
    _description = 'Import SF Opportunity into sale.order model'

    openerp_id = fields.Many2one('sale.order',
                                 string='Sale Order Line',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('sf_id_uniq', 'unique(backend_id, salesforce_id)',
         'A sales order with same Salesforce identifier already exists.')
    ]

SalesforceBinder._model_name.append('connector.salesforce.opportunity')


class SalesforceOpportunityLineItem(models.Model):
    _inherit = 'salesforce.binding'
    _inherits = {'sale.order.line': 'openerp_id'}
    _name = 'connector.salesforce.opportunity.line.item'
    _description = 'Import SF Opportunity line item into sale.order model'

    openerp_id = fields.Many2one('sale.order.line',
                                 string='Sale Order Line',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('sf_id_uniq', 'unique(backend_id, salesforce_id)',
         'A sales order line with same Salesforce identifier already exists.')
    ]

SalesforceBinder._model_name.append(
    'connector.salesforce.opportunity.line.item')
