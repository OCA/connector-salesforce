# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp.addons.connector.unit.mapper import ExportMapper
from openerp.addons.connector.unit.mapper import mapping
from ..backend import salesforce_backend
from ..unit.exporter_synchronizer import (SalesforceDelayedBatchSynchronizer,
                                          SalesforceDirectBatchSynchronizer,
                                          SalesforceExportSynchronizer)

_logger = logging.getLogger(__name__)

TYPE_MAP_REGISTER = {'Service': 'service'}


@salesforce_backend
class SalesforceProductExporter(SalesforceExportSynchronizer):
    _model_name = 'connector.salesforce.product'

    def _to_deactivate(self):
        """Implement predicate that decide if product
        must be deactivated in Odoo
        """
        assert self.binding
        if not self.binding.active or not self.binding.sale_ok:
            return True
        return False


@salesforce_backend
class SalesforceDirectBatchProductExporter(SalesforceDirectBatchSynchronizer):
    _model_name = 'connector.salesforce.product'


@salesforce_backend
class SalesforceDelayedBatchProductExporter(
        SalesforceDelayedBatchSynchronizer):
    _model_name = 'connector.salesforce.product'


@salesforce_backend
class SalesforceProductMapper(ExportMapper):
    _model_name = 'connector.salesforce.product'

    direct = [
        ('active', 'IsActive',),
        ('code', 'ProductCode'),
        ('description', 'Description'),
        ('name', 'Name'),
    ]

    @mapping
    def product_type(self, record):
        backend = record.backend_id
        mapping = {rec.product_type: rec.sf_family
                   for rec in backend.sf_product_type_mapping_ids}
        family = mapping.get(record.type)
        if not family:
            return {}
        return {'Family': family}
