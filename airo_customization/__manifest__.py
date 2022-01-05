# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Airogroup Constomization',
    'summary': '''Airogroup customization''',
    'description': '''Airogroup customization''',
    'author': 'Aardug, Arjan Rosman',
    'website': 'http://www.aardug.nl/',
    'support': 'arosman@aardug.nl',
    'version': '15.0.0',
    'category': 'mrp',
    'depends': ['mrp'],
    'data': [
        'views/mrp_view.xml',
    ],
    'description': '''
	              1) In the Product Price List If the fixed price is set to 0 then raise User Error.
                  2) Add Lot Number in Stock Move
                  3) State is changed based on confirming Manufacture order
      ''',
    'installable': True,
    'application': False,
    'license': 'LGPL-3'
}
