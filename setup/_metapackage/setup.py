import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-connector-salesforce",
    description="Meta package for oca-connector-salesforce Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-connector_salesforce',
        'odoo8-addon-connector_salesforce_server_environment',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
