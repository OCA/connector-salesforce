# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Provides various date/datetime helper"""
import datetime
import pytz
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


def convert_to_utc_datetime_with_tz(datetime_str):
    """Convert a naive Odoo datetime string
    into a :py:class:`datetime.datetime` with utc time zone

    :param datetime_str: Odoo datetime string
    :type datetime_str: str

    :return: return a datetime with tz correspnding to string parameter
    :trype: `datetime.datetime`
    """
    d_time = datetime.datetime.strptime(datetime_str,
                                        DEFAULT_SERVER_DATETIME_FORMAT)
    return pytz.utc.localize(d_time)
