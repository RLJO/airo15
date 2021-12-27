# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

{
    'name': 'Disable Quick Product Creation',
    'version': "15.0.1.0",
    "summary": """Disable Product Creation On Sales | Disable Product Creation On Invoice | Disable Product Creation On Purchase | Disable | Quick create | Product | Sales | Purchase | Invoice | Stop Create | Purchase Order Lines | Sales Order Lines | Customer Invoice Lines | Supplier Invoice Lines""",
    "description": """
    """,
    'author': 'TidyWay',
    'website': 'http://www.tidyway.in',
    'category': 'product',
    'depends': ['sale', 'account', 'purchase'],
    'data': [
             'views/purchase.xml',
             'views/sale.xml',
             'views/invoice.xml',
             ],
    'price': 20,
    'currency': 'EUR',
    'installable': True,
    'license': 'OPL-1',
    'application': True,
    'auto_install': False,
    'images': ['images/label.jpg'],
    'live_test_url': 'https://youtu.be/o_YM6qjc1Qk'
}
