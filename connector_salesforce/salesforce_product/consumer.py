# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector.event import (on_record_write,
                                            on_record_create,
                                            on_record_unlink)
from ..consumer import delay_export, delay_deactivate
from ..unit.binder import SalesforceBinder


@on_record_create(model_names='connector.salesforce.product')
def export_sf_product(session, model_name, record_id, vals=None):
    """ Delay a job which export a product binding record.
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
    if record.backend_id.sf_product_master == 'erp':
        delay_export(session, model_name, record_id)


@on_record_unlink(model_names='connector.salesforce.product')
def deactivate_product(session, model_name, record_id):
    """ Delay a job which deactivate a binding product record
    on Salesforce

    :param session: current session
    :type session: :py:class:`openerp.addons.connector.
                              session.ConnectorSession`

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :record_id: The id of the binding model record
    :type record_id: int or long
    """

    record = session.env[model_name].browse(record_id)
    if record.backend_id.sf_product_master == 'erp':
        delay_deactivate(session, model_name, record_id)


@on_record_create(model_names='product.product')
def create_product_binding(session, model_name, record_id, vals=None):
    """Create a binding entry for newly created product
    :param session: current session
    :type session: :py:class:`openerp.addons.connector.
                              session.ConnectorSession`

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :record_id: The id of the binding model record
    :type record_id: int or long
    """

    record = session.env[model_name].browse(record_id)
    sf_product_model = 'connector.salesforce.product'
    backend_model = 'connector.salesforce.backend'
    backends = session.env[backend_model].search([])
    if not record.sale_ok or not record.active:
        return
    for backend in backends:
        if backend.sf_product_master == 'erp':
            session.env[sf_product_model].create(
                {'backend_id': backend.id,
                 'openerp_id': record.id}
            )


@on_record_write(model_names='product.product')
def export_product(session, model_name, record_id, vals=None):
    """ Delay a job which export a binding record
    when related product is edited
    :param session: current session
    :type session: :py:class:`openerp.addons.connector.
                              session.ConnectorSession`

    :param model_name: name of the binding model.
                       In our case `connector.salesforce.xxx`
    :type model_name: str

    :record_id: The id of the binding model record
    :type record_id: int or long
    """
    sf_product_model = 'connector.salesforce.product'
    backend_model = 'connector.salesforce.backend'
    backends = session.env[backend_model].search([])
    for backend in backends:
        if backend.sf_product_master == 'erp':
            conn_env = backend.get_connector_environment(
                sf_product_model
            )
            product_binder = conn_env.get_connector_unit(
                SalesforceBinder
            )
            sf_prod = product_binder.to_binding(
                record_id
            )
            if sf_prod:
                export_sf_product(
                    session,
                    sf_product_model,
                    sf_prod.id,
                    vals=vals
                )
