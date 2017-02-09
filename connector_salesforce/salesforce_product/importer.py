# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp.addons.connector.unit.mapper import ImportMapper
from openerp.addons.connector.unit.mapper import mapping, only_create
from ..backend import salesforce_backend
from ..unit.importer_synchronizer import (SalesforceDelayedBatchSynchronizer,
                                          SalesforceDirectBatchSynchronizer,
                                          SalesforceImportSynchronizer)

_logger = logging.getLogger(__name__)

TYPE_MAP_REGISTER = {'Service': 'service'}


@salesforce_backend
class SalesforceProductImporter(SalesforceImportSynchronizer):
    _model_name = 'connector.salesforce.product'


@salesforce_backend
class SalesforceDirectBatchProductImporter(SalesforceDirectBatchSynchronizer):
    _model_name = 'connector.salesforce.product'


@salesforce_backend
class SalesforceDelayedBatchProductImporter(
        SalesforceDelayedBatchSynchronizer):
    _model_name = 'connector.salesforce.product'


@salesforce_backend
class SalesforceProductMapper(ImportMapper):
    _model_name = 'connector.salesforce.product'

    direct = [
        ('IsActive', 'active'),
        ('ProductCode', 'code'),
        ('Description', 'description'),
        ('Name', 'name'),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def sale_ok(self, record):
        return {'sale_ok': True}

    @mapping
    def product_type(self, record, **kwargs):
        family = record.get('Family')
        mapping = {rec.sf_family: rec.product_type
                   for rec in self.backend_record.sf_product_type_mapping_ids}
        product_type = mapping.get(family)
        if not product_type:
            return {}
        return {'type': product_type}
