# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            product_id = self.env['product.template'].search([('id', '=', values.get('product_tmpl_id'))])
            if product_id.website_id:
                if values.get('fixed_price') == 0.000:
                    raise UserError(_('Price is not set'))
        return super(PricelistItem, self).create(vals_list)

    def write(self, values):
        res = super(PricelistItem, self).write(values)
        product_id = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
        if product_id.website_id:
            if self.fixed_price == 0.0 or values.get('fixed_price') == 0:
                raise UserError(_('Price is not set'))
        return res