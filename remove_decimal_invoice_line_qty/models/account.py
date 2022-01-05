# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################


from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent(self):
        res = super(AccountMove, self).action_invoice_sent()
        model_id = self.env['ir.model'].search([('model', '=', 'account.move')], limit=1)
        template = self.env['mail.template'].search([('model_id', '=', model_id.id)], limit=1)
        if template:
            res['context']['default_template_id'] = template.id
        return res
