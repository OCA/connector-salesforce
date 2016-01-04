# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2014-2015 Camptocamp SA
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
{'name': 'Salesforce Connector',
 'version': '7.0.1.0.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp,Odoo Community Association (OCA)',
 'category': 'Connector',
 'complexity': "normal",
 'depends': ['connector', 'sale', 'product'],
 'summary': """Provides core import export interfaces with Salesforce.""",
 'description': """see README.rst""",
 'data': [
     'salesforce_backend/view/backend_model_view.xml',
     'salesforce_account/view/backend_view.xml',
     'salesforce_contact/view/backend_view.xml',
     'salesforce_contact/view/res_partner_view.xml',
     'salesforce_product/view/backend_view.xml',
     'salesforce_price_book_entry/view/backend_view.xml',
     'salesforce_opportunity/view/backend_view.xml',
     'security/ir.model.access.csv',
     'data/cron.xml',
 ],
 'external_dependencies': {'python': ['simple_salesforce', 'requests']},
 'test': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 }
