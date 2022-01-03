# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models


class ConnectorShopMapping(models.Model):
    _name = "connector.shop.mapping"
    _inherit = ['connector.common.mapping']
    _order = 'id desc'
    _description = "Ecomm Shop"

    base_url = fields.Char('Shop Url')
    name = fields.Char('Shop Name')
    opencart_shop = fields.Char('Opencart Shop Id')