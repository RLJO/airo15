# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    xaa_ar_batch_no = fields.Char(string='Batch No')
    xaa_ar_lot = fields.Char(string='Lot/Serial Number')
