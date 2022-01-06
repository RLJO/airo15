# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        if self._context.get('params') and self._context.get('params')['model'] == 'sale.order':
            self.state = 'draft'
        return res

    def action_assign(self):
        res = super(MrpProduction, self).action_assign()
        for production in self:
            for move in production.move_raw_ids:
                lot_list = []
                for line in move.move_line_ids:
                    if line.lot_id:
                        lot_list.append(line.lot_id.name)
                move.xaa_ar_lot = ','.join(lot_list)
        return res
