# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector import backend

salesforce_backend = backend.Backend('salesforce')
salesforce_backend_v15 = backend.Backend(parent=salesforce_backend,
                                         version="15")
