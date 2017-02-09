# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector.exception import (ConnectorException,
                                                RetryableJobError)


class SalesforceRESTAPIError(ConnectorException):
    """Rest API error"""


class SalesforceSecurityError(SalesforceRESTAPIError):
    """Authentication error with Salesforce"""


class SalesforceResponseError(SalesforceRESTAPIError):
    """Map simple_salesforce error to connector error"""
    def __init__(self, sf_error):
        """Override to store simple_salesforce error"""
        self.sf_error = sf_error
        self.message = repr(sf_error)


class SalesforceSessionExpiredError(RetryableJobError):
    """Authentication error with Salesforce"""


class SalesforceQuotaError(RetryableJobError):
    """To be used when API call quota is consumed to postpone the job"""
