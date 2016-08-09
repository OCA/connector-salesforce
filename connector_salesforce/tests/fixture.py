# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Salesforce API fixture data"""
contact = {
    'Id': 'uuid_contact_01',
    'MailingStreet': 'Contact street',
    'MailingPostalCode': 'Contact zip',
    'MailingCity': 'Contact city',
    'MailingState': 'Contact state',
    'MailingCountryCode': 'CH',
    'Fax': '+41 21 619 10 10',
    'Phone': '+41 21 619 10 12',
    'Title': 'Contact function',
    'OtherPhone': '+41 21 619 10 13',
    'MobilePhone': '+41 21 619 10 14',
    'AssistantPhone': '+41 21 619 10 15',
    'Email': 'contact@mail.ch',
    'AccountId': 'uuid_account_01',
    'LastName': 'Contact lastname',
    'FirstName': 'Contact firstname',
}

account = {
    'Id': 'uuid_account_01',
    'Name': 'Main name',
    'BillingStreet': 'Main street',
    'BillingPostalCode': 'Main zip',
    'BillingCity': 'Main city',
    'BillingState': 'Main state',
    'BillingCountryCode': 'CH',
    'Fax': '+41 21 619 10 10',
    'Phone': '+41 21 619 10 12',
    'VATNumber__c': 'Main vat',
    'ShippingStreet': 'Shipping street',
    'ShippingPostalCode': 'Shipping zip',
    'ShippingCity': 'Shipping city',
    'ShippingState': 'Shipping state',
    'ShippingCountryCode': 'CH',
    'CurrencyIsoCode': 'EUR',
}

price_book_entry = {
    'Id': 'uuid_pricebookentry_01',
    'UnitPrice': 200.0,
    'CurrencyIsoCode': 'EUR',
    'Product2Id': 'uuid_product_01',
}

opportunity = {
    'Id': 'uuid_opportunity_01',
    'AccountId': 'uuid_account_01',
    'CurrencyIsoCode': 'EUR',
    'Name': 'A won opportunity',

}

opportunity_line = {
    'Id': 'uuid_opportunityline_01',
    'Discount': 20,
    'Description': 'A sale',
    'ListPrice': 100.0,
    'Quantity': 2.0,
    'OpportunityId': 'uuid_opportunity_01',
}
