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
from openerp.addons.connector.unit.mapper import ImportMapper
from openerp.addons.connector.exception import MappingError


class AddressMapper(ImportMapper):

    def _state_id(self, record, state_key, country_key):
        """Map to Odoo state from Salesforce
        state and country code
        """
        state_name = record.get(state_key)
        if not state_name:
            return False
        state = self.session.env['res.country.state'].search(
            [('name', '=', state_name)],
            limit=1,
        )
        if state:
            return state.id
        else:
            country_id = self._country_id(record, country_key)
            if country_id:
                return self.session.env['res.country.state'].create(
                    {'name': state_name,
                     'code': state_name[0:3],
                     'country_id': country_id}
                ).id
        return False

    def _country_id(self, record, country_key):
        """Map Salesforce countrycode to Odoo code"""
        country_code = record.get(country_key)
        if not country_code:
            return False
        country = self.session.env['res.country'].search(
            [('code', '=', country_code)]
        )
        # we tolerate the fact that country is null
        if len(country) > 1:
            raise MappingError(
                'Many countries found to be linked with partner %s' % record
            )

        if not country:
            raise MappingError(
                "No country %s found when mapping partner %s" % (
                    country_code,
                    record
                )
            )
        return country.id

    def _title_id(self, record, title_key):
        """Map the Odoo title from Salesforce title code
        If not available create it
        """
        title_name = record.get(title_key)
        if not title_name:
            return False
        title = self.session.env['res.partner.title'].search(
            [('name', '=', title_name)],
        )
        if len(title) > 1:
            raise MappingError(
                'Many titles found to be linked with partner %s' % record
            )
        if title:
            return title.id
        return self.model.create({'name': title_name}).id


class PriceMapper(ImportMapper):

    def get_currency_id(self, record):
        """Mapp the Odoo currency from the Salesforce currency code"""
        currency_iso_code = record.get('CurrencyIsoCode')
        if not currency_iso_code:
            raise MappingError(
                'No currency Given for: %s' % record
            )
        currency = self.session.env['res.currency'].search(
            [('name', '=ilike', currency_iso_code)]
        )
        if not currency:
            raise MappingError(
                'No %s currency available. '
                'Please create one manually' % currency_iso_code
            )
        if len(currency) > 1:
            raise ValueError(
                'Many Currencies found for %s. '
                'Please ensure your multicompany rules are corrects '
                'or check that the job is not runned by '
                'the admin user' % currency_iso_code
            )
        return currency.id
