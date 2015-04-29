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
from collections import namedtuple
from openerp.addons.server_environment import serv_config
from openerp import models, fields

AuthField = namedtuple('AuthField', ['name', 'is_mandatory'])


class salesforce_backend(models.Model):
    """Use server env. to manage auth parameters"""

    def _get_auth_columns(self):
        return [
            AuthField('authentication_method', True),
            AuthField('url', True),
            AuthField('sandbox', True),
        ]

    def _get_env_auth_data(self):
        for backend in self:
            section_data = {}
            section_name = "salesforce_auth_%s" % backend.name
            if not serv_config.has_section(section_name):
                raise ValueError(
                    'Section %s does not exists' % section_name
                )
            for col in self._get_auth_columns():
                if serv_config.has_option(section_name, col.name):
                    section_data[col.name] = serv_config.get(section_name,
                                                             col.name)
                else:
                    section_data[col.name] = False
                if col.is_mandatory and not section_data.get(col.name):
                    raise ValueError(
                        'Key %s not set in config file for section %s' % (
                            col.name,
                            section_name
                        )
                    )
                if section_data[col.name] in serv_config._boolean_states:
                    section_data[col.name] = serv_config._boolean_states[
                        section_data[col.name]
                    ]
                for key, value in section_data.iteritems:
                    setattr(backend, key, value)

    _inherit = "connector.salesforce.backend"

    authentication_method = fields.Char(
        compute='_get_env_auth_data',
        string='Authentication Method',
    )

    url = fields.Char(
        compute='_get_env_auth_data',
        string='URL',
    )

    sandbox = fields.Boolean(
        compute='_get_env_auth_data',
        string='Connect on sandbox instance',
    )
