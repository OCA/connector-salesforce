# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import namedtuple
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import ImportSynchronizer
from openerp.addons.connector.exception import IDMissingInBackend
from ..unit.rest_api_adapter import with_retry_on_expiration

_logger = logging.getLogger(__name__)

ImportSkipReason = namedtuple('SkipReason', ['should_skip', 'reason'])


class SalesforceImportSynchronizer(ImportSynchronizer):

    def __init__(self, connector_env):
        """Constructor"""
        super(SalesforceImportSynchronizer, self).__init__(connector_env)
        self.salesforce_id = None
        self.salesforce_record = None

    def _after_import(self, binding):
        """ Hook called after the import"""
        return

    def _before_import(self):
        """ Hook called before the import"""
        return

    def _create(self, data):
        """Implements the creation of record in Odoo

        :param data: mapped dic of data to be used by
                     :py:meth:``models.Model.create``
        :type data: dict

        :return: the create id of the Odoo binding
        :rtype: int or long
        """
        return self.model.create(data)

    def _to_deactivate(self):
        """Hook to check if record must be deactivated"""
        return False

    def _deactivate(self):
        """Implementation of an Odoo binding record deactivation
        It By default it will lookup for an active column and
        set it value to True. If no active column is available
        it will raise a :py:class:`NotImplementedError`
        """
        assert self.salesforce_id
        cols = set(self.model._fields)
        if 'active' not in cols:
            raise NotImplementedError(
                'Model %s does not have an active field. '
                'custom _deactivate must be implemented'
            )
        current_id = self.binder.to_openerp(self.salesforce_id)
        self.model.browse(current_id).write({'active': False})

    def _get_record(self, raise_error=False):
        """Return a dict representation of a currently
        imported Salesforce record as provided by the REST adapter

        :return: a dict representation of a currently
                 imported Salesforce record as provided by the REST adapter
        :rtype: dict
        """
        rec = None
        if self.backend_adapter.exists(self.salesforce_id):
            rec = self.backend_adapter.read(self.salesforce_id)
        elif raise_error:
            raise IDMissingInBackend(
                'id %s does not exists in Salesforce for %s' % (
                    self.backend_adapter._sf_type
                )
            )
        return rec

    def _map_data_for_update(self, mapper, **kwargs):
        """ Call the convert function of the Mapper

        in order to get converted record by using
        mapper.data or mapper.data_for_create

        :return: mapped dict of data to be used by
                 :py:meth:``models.Model.create``
        :rtype: dict
        """
        data = mapper.values(**kwargs)
        return data

    def _map_data_for_create(self, mapper, **kwargs):
        """ Call the convert function of the Mapper

        in order to get converted record by using
        mapper.data or mapper.data_for_create

        :return: mapped dict of data to be used by
                 :py:meth:``models.Model.create``
        :rtype: dict
        """
        data = mapper.values(for_create=True, **kwargs)
        return data

    def _must_skip(self):
        """Decide if the current record should
        not be imported. By default it return
        a False :py:class:`ImportSkipReason`

        :return: a :py:class:`ImportSkipReason`
        :rtype: :py:class:`ImportSkipReason`
        """
        return ImportSkipReason(should_skip=False, reason=None)

    def _update(self, binding, data):
        """Implement the update of a binding record
        that is already existing in Odoo

        :param binding: the Odoo record to export
        :type binding: RecordSet

        :param data: mapped dict of data to be used by
                     :py:meth:``models.Model.create``
        """
        binding.ensure_one()
        binding.write(data)

    def _validate_data(self, data):
        """ Check if the values to import are correct

        :param data: data to validate
        Proactively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.

        Raise `InvalidDataError`
        """
        # we may want to return an NotImplementedError
        return

    def _import(self, binding):
        """Try Import or update a binding record from Salesforce using REST API
        :param binding: the current binding record in Odoo
        :type binding: RecordSet
        """
        record_mapper = self.mapper.map_record(self.salesforce_record)
        if binding:
            binding.ensure_one()
            # optimisation trick to avoid lookup binding
            data = self._map_data_for_update(
                record_mapper,
                binding=binding,
            )
            self._validate_data(data)
            self._update(binding, data)
        else:
            data = self._map_data_for_create(
                record_mapper,
                binding=binding,
                backend_record=self.backend_record
            )
            self._validate_data(data)
            binding = self._create(data)
        self.binder.bind(self.salesforce_id, binding)
        self._after_import(binding)

    def run(self, salesforce_id, force_deactivate=False):
        """Try to import or update a record on Salesforce using REST API
        call required hooks and bind the record

        :param salesforce_id: the current Salesforce UUID to import
        :type salesforce_id: str

        :param force_deactivate: If set to True it will force deactivate
                           without calling _to_deactivate
                           mostly use to save some REST calls
        """
        self.salesforce_id = salesforce_id
        # if we force deactivation there is no
        # need to read record in Salesforces
        # it save some REST calls
        if force_deactivate:
            self._deactivate()
            return
        self.salesforce_record = self._get_record()
        if not self.salesforce_record:
            # Record deleted in backend so nothing to import
            return
        skip = self._must_skip()
        if skip.should_skip:
            return skip.reason
        if self._to_deactivate():
            self._deactivate()
            return
        self._before_import()
        binding = self.binder.to_openerp(self.salesforce_id)
        if binding:
            binding.ensure_one()
        # calls _after_import
        self._import(binding)


class SalesforceBatchSynchronizer(ImportSynchronizer):

    def before_batch_import(self):
        pass

    def after_batch_import(self):
        pass

    def run(self, date=False):
        self.before_batch_import()
        salesforce_ids = self.backend_adapter.get_updated(date)
        for salesforce_id in salesforce_ids:
            self._import_record(salesforce_id)
        salesforce_ids = self.backend_adapter.get_deleted(date)
        for salesforce_id in salesforce_ids:
            self._deactivate_record(salesforce_id)
        self.after_batch_import()

    def _import_record(self, salesforce_id):
        """ Import a record directly or delay the import of the record.
        Method to implement in sub-classes.
        """
        raise NotImplementedError

    def _deactivate_record(self, salesforce_id):
        """ Import a record directly or delay the import of the record.
        Method to implement in sub-classes.
        """
        raise NotImplementedError


class SalesforceDelayedBatchSynchronizer(SalesforceBatchSynchronizer):

    def _import_record(self, salesforce_id):
        "Try to import a Salesforce record in Odoo using Jobs"
        import_record.delay(self.session,
                            self.model._name,
                            self.backend_record.id,
                            salesforce_id)

    def _deactivate_record(self, salesforce_id):
        "Try to deactivate a Salesforce deactivated record in Odoo using Jobs"
        deactivate_record.delay(self.session,
                                self.model._name,
                                self.backend_record.id,
                                salesforce_id)


class SalesforceDirectBatchSynchronizer(SalesforceBatchSynchronizer):

    def _import_record(self, salesforce_id):
        "Try to import a Salesforce record in Odoo directly"
        import_record(self.session,
                      self.model._name,
                      self.backend_record.id,
                      salesforce_id)

    def _deactivate_record(self, salesforce_id):
        "Try to deactivate a Salesforce deactivated record directly"
        deactivate_record(self.session,
                          self.model._name,
                          self.backend_record.id,
                          salesforce_id)


@with_retry_on_expiration
def batch_import(session, model_name, backend_id, date=False):
    """import all candidate Salesforce records In Odoo for a given
    backend, model and date

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :param backend_id: id of current backend
    :type backend_id: id or long

    :param date: Odoo date string to do past lookup
    :type date: str
    """
    backend = session.env['connector.salesforce.backend'].browse(
        backend_id
    )
    connector_env = backend.get_connector_environment(model_name)
    importer = connector_env.get_connector_unit(
        SalesforceDirectBatchSynchronizer
    )
    importer.run(date=date)


@with_retry_on_expiration
def delayed_batch_import(session, model_name, backend_id, date=False):
    """import all candidate Salesforce records In Odoo for a given
    backend, model and date using jobs

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :param backend_id: id of current backend
    :type backend_id: id or long

    :param date: Odoo date string to do past lookup
    :type date: str
    """
    backend = session.env['connector.salesforce.backend'].browse(
        backend_id
    )
    connector_env = backend.get_connector_environment(model_name)
    importer = connector_env.get_connector_unit(
        SalesforceDelayedBatchSynchronizer
    )
    importer.run(date=date)


@job
def import_record(session, model_name, backend_id, salesforce_id):
    """Import a Salesforce record in Odoo for a given
    backend, model and Salesforce uuid

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :param backend_id: id of current backend
    :type backend_id: id or long

    :param salesforce_id: the uuid of Salesforce record
    :type salesforce_id: str
    """
    backend = session.env['connector.salesforce.backend'].browse(
        backend_id
    )
    connector_env = backend.get_connector_environment(model_name)
    importer = connector_env.get_connector_unit(
        SalesforceImportSynchronizer
    )
    importer.run(salesforce_id)
    return "%s record with Salesforce id %s imported" % (model_name,
                                                         salesforce_id)


@job
def deactivate_record(session, model_name, backend_id, salesforce_id):
    """deactivate a Salesforce record in Odoo for a given
    backend, model and Salesforce uuid

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :param backend_id: id of current backend
    :type backend_id: id or long

    :param salesforce_id: the uuid of Salesforce record
    :type salesforce_id: str
    """
    backend = session.env['connector.salesforce.backend'].browse(
        backend_id
    )
    connector_env = backend.get_connector_environment(model_name)
    importer = connector_env.get_connector_unit(
        SalesforceImportSynchronizer
    )
    importer.run(salesforce_id, force_deactivate=True)
    return "%s record with Salesforce id %s deactivated" % (model_name,
                                                            salesforce_id)
