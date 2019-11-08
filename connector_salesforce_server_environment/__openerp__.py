# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Connector Salesforce Server Environment',
 'version': '8.0.1.0.0',
 'author': 'Camptocamp, Odoo Community Association (OCA)',
 'category': 'Tools',
 'depends': ['server_environment', 'connector_salesforce'],
 'description': """Implements server environment behavior
for connector Salesforce authentication.

To use it you have to add a section named as:

    salesforce_auth + Name of the backend

Default available section options are:

- authentication_method
- callback_url
- sandbox
- url

Module can easily be extended to add any other field.
By default they are not provided in order not have security issues.
 """,
 'website': 'http://www.camptocamp.com',
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 }
