# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Aardug. (Website: www.aardug.nl).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, models, _


class QualityCheck(models.Model):
    _inherit = "quality.check"

    @api.depends('measure_success')
    def _compute_warning_message(self):
        for rec in self:
            if rec.measure_success == 'fail':
                rec.warning_message = (
                    'You measured %.3f %s and it should be between %.3f\
                     and %.3f %s.') % (
                    rec.measure, rec.norm_unit, rec.point_id.tolerance_min,
                    rec.point_id.tolerance_max, rec.norm_unit
                )
            else:
                rec.warning_message = ''
