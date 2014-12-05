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
from __future__ import absolute_import
from openerp import fields
from openerp.addons.connector.exception import ManyIDSInBackend
from openerp.addons.connector.connector import Binder
from ..backend import salesforce_backend


@salesforce_backend
class SalesforceBinder(Binder):
    """ Manage bindings between Models identifier and Salesforce identifier"""
    _model_name = []

    def to_openerp(self, salesforce_id, unwrap=False):
        """Returns the Odoo id for an external ID""

        :param salesforce_id: salesforce_id row unique idenifier
        :type salesforce_id: str

        :param unwrap: If True returns the id of the record related
                       to the binding record

        :return: binding record  or if unwrapped the record related
                 to the binding record
        :rtype: RecordSet
        """

        binding = self.model.with_context(active_search=False).search(
            [('salesforce_id', '=', salesforce_id),
                ('backend_id', '=', self.backend_record.id)],

        )
        if not binding:
            return None
        assert len(binding) == 1, "Several records found: %s" % binding
        if unwrap:
            return binding.openerp_id
        else:
            return binding

    def to_backend(self, binding_id):
        """Return the external code for a given binding model id

        :param binding_id: id of a binding model
        :type binding_id: int

        :return: external code of `binding_id` or None
        """
        sf_record = self.model.read(
            binding_id,
            ['salesforce_id']
        )
        if not sf_record:
            return None
        return sf_record['salesforce_id']

    def to_binding(self, record):
        """Return the binding record for a given openerp record and backend

        :param record: record or id of a Odoo record
        :type binding_id: record or id

        :return: external binding record for `record` or None
        """
        lookup_id = record if isinstance(record, (int, long))else record.id
        sf_id = self.model.search(
            [
                ('backend_id', '=', self.backend_record.id),
                ('openerp_id', '=', lookup_id)
            ]
        )
        if not sf_id:
            return None
        if len(sf_id) > 1:
            raise ManyIDSInBackend(
                'Many record found in backend %s for model %s record_id %s' %
                (self.backend_record.name, self.model._name, record)
            )
        return sf_id

    def bind(self, salesforce_id, binding):
        """ Create the link between an external id and an Odoo row and
        by updating the last synchronization date and the external code.

        :param external_id: Salesforce unique identifier
        :param binding: Binding record
        :type binding: binding record
        """
        # avoid to trigger the export when we modify the `odbc code`
        now_fmt = fields.Datetime.now()
        binding.with_context(connector_no_export=True).write(
            {'salesforce_id': salesforce_id,
             'salesforce_sync_date': now_fmt},
        )
