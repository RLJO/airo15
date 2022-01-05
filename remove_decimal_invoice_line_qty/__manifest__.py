# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': "Remove decimal from invoice line quantity",
    'summary': """""",
    'description': """Remove decimal from quantity field of invoice line""",
    'author': "Aardug, Arjan Rosman",
    'website': "http://www.aardug.nl/",
    'support': 'arosman@aardug.nl',
    'version': '15.0.0',
    'category': 'Account',
    'depends': ['account','sale'],
    'installable': True,
    'application': False,
    'data': [
            'views/account_move_view.xml',
            'views/sale_order_view.xml',
            ],
    'license':'LGPL-3',
}
