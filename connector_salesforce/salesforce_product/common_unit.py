# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..backend import salesforce_backend
from ..unit.rest_api_adapter import SalesforceRestAdapter


@salesforce_backend
class SalesforceProductAdapter(SalesforceRestAdapter):
    _model_name = 'connector.salesforce.product'
    _sf_type = 'Product2'

    def delete(self, salesforce_id):
        """Override adapter to write on
        the IsActive key of product instead of
        doing a call to the delete API function
        and send product to recycle bin
        """
        # Product model as an `IsActive` key
        return self.write(salesforce_id, {'IsActive': False})
