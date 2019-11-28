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
from openerp.osv import orm, fields
from ..unit.binder import SalesforeceBinder


class SalesforceOpportunity(orm.Model):
    _inherit = 'salesforce.binding'
    _inherits = {'sale.order': 'openerp_id'}
    _name = 'connector.salesforce.opportunity'
    _description = 'Import SF Opportunity into sale.order model'

    _columns = {
        'openerp_id': fields.many2one('sale.order',
                                      string='Sale Order Line',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
    }

    _sql_contraints = [
        ('sf_id_uniq', 'unique(backend_id, salesforce_id)',
         'A Sale Order with same Salesforce id already exists')
    ]

SalesforeceBinder._model_name.append('connector.salesforce.opportunity')

class SalesforceOpportunityLineItem(orm.Model):
    _inherit = 'salesforce.binding'
    _inherits = {'sale.order.line': 'openerp_id'}
    _name = 'connector.salesforce.opportunity.line.item'
    _description = 'Import SF Opportunity line item into sale.order model'

    _columns = {
        'openerp_id': fields.many2one('sale.order.line',
                                      string='Sale Order Line',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
    }

    _sql_contraints = [
        ('sf_id_uniq', 'unique(backend_id, salesforce_id)',
         'A Sale Order Line with same Salesforce id already exists')
    ]

SalesforeceBinder._model_name.append('connector.salesforce.opportunity.line.item')
