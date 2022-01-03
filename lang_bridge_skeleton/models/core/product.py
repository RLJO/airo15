# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
#
##############################################################################

from odoo import api,fields, models
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	meta_tag_title = fields.Char(string="Meta Tag Title",translate = True)
	meta_tag_description = fields.Char(string="Meta Tag Description",translate = True)
	meta_tag_keyword = fields.Char(string="Meta Tag Keywords",translate = True)
	product_tag = fields.Char(string = "Product Tags",translate = True)
	oc_description = fields.Text(string = "Product Description",translate = True)