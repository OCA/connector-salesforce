# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .unit.exporter_synchronizer import export_record, deactivate_record


def delay_export(session, model_name, record_id):
    """ Delay a job which export a binding record.
    :param session: current session
    :type session: :py:class:`openerp.addons.connector.
                              session.ConnectorSession`

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :record_id: The id of the binding model record
    :type record_id: int or long
    """
    record = session.env[model_name].browse(
        record_id
    )
    export_record.delay(
        session,
        model_name,
        record.backend_id.id,
        record_id
    )


def delay_deactivate(session, model_name, record_id):
    """ Delay a job which deactivate a binding record.

    :param session: current session
    :type session: :py:class:`openerp.addons.connector.
                              session.ConnectorSession`

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :record_id: The id of the binding model record
    :type record_id: int or long
    """
    record = session.env[model_name].browse(
        record_id
    )
    deactivate_record.delay(
        session,
        model_name,
        record.backend_id.id,
        record_id
    )
