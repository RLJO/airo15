# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': "Add note in invoice report",
    'summary': """Add note in invoice report based on fiscal position""",
    'description': """Add note in invoice report based on fiscal position""",
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
            ],
    'license': 'LGPL-3',
}
