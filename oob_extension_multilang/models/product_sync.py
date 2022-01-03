# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

# Product Sync Operation
import json
from odoo import api, models
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class ConnectorSnippet(models.TransientModel):
	_inherit = "connector.snippet"

	def _export_opencart_specific_template(self , obj_pro, instance_id, channel, connection):
		"""
		@param code: Obj pro, instance id , channel , connection
		@param context: A standard dictionary
		@return: Dictionary
		"""
		session_key = connection.get('session_key', False)
		opencart = connection.get('opencart',False)
		url = connection.get('url',False)
		product_configurable =  connection.get('product_configurable', False)
		status = False
		ecomm_id = False
		oc_categ_id = 0
		option_id = False
		product_data = {}
		is_variants = False
		error = ''
		ctx = self._context.copy() or {}
		lang_data = False
		if obj_pro and session_key and opencart and url:
			try:
				if product_configurable =='variants':
					product_data = self.get_product_variant_data(obj_pro , instance_id)
					if 'oc_option_value_ids' in product_data:
						is_variants = True
				else:
					product_data['variant_id'] = str(
						obj_pro.product_variant_ids[0].id)
				oc_categ_id = 0
				prod_catg = []
				for j in obj_pro.connector_categ_ids.categ_ids:
					oc_categ_id = self.sync_categories(j , instance_id, channel, connection )
					prod_catg.append(oc_categ_id)
				if obj_pro.categ_id.id:
					oc_categ_id = self.sync_categories(obj_pro.categ_id, 
													instance_id ,channel, connection)
					prod_catg.append(oc_categ_id)
				product_data['sku'] = obj_pro.default_code or 'Ref Odoo %s' % obj_pro.id
				product_data['model'] = obj_pro.default_code or 'Ref Odoo %s' % obj_pro.id
				if ctx.get('translation_sync'):
					lang_data = ctx.get('translated_values', False)
				if lang_data:
					product_data['lang_description'] = {}
					for lang_id, lang_values in lang_data.items():
						product_data['lang_description'].update({
							lang_id:{'name':lang_values['name'],
								'keyword': lang_values['name'],
								'description': lang_values['description'] or ' ',
								'meta_description':lang_values['meta_tag_description'] or '',
								'meta_keyword':lang_values['meta_tag_keyword'] or '',
								'meta_title':lang_values['meta_tag_title'] or '',
								'tag':lang_values['tag'] or '',
								}})
				product_data['name'] = obj_pro.name
				product_data['keyword'] = obj_pro.name
				product_data['description'] = obj_pro.oc_description or ' '
				product_data['meta_description'] = obj_pro.meta_tag_description or ' '
				product_data['meta_keyword'] = obj_pro.meta_tag_keyword or ' '
				product_data['meta_title'] = obj_pro.meta_tag_title or ' '
				product_data['tag'] = obj_pro.product_tag or ' '
				product_data['ean'] = obj_pro.barcode or ' '
				product_data['price'] = obj_pro.list_price or 0.00
				product_data['quantity'] = self.env['connector.snippet'].get_quantity(obj_pro.product_variant_ids[0], instance_id)
				product_data['weight'] = obj_pro.weight or 0.00
				product_data['erp_product_id'] = obj_pro.id
				product_data['product_category'] = list(set(prod_catg))
				product_data['erp_template_id'] = obj_pro.id
				product_data['product_image'] = obj_pro.image_1920
				product_data['minimum'] = '1'
				product_data['subtract'] = '1'
				if product_data['product_image']:
					product_data['product_image'] = product_data['product_image'].decode()
				product_data['manufacturer_id'] = self.check_specific_brand(obj_pro.product_brand_id, connection, instance_id) or ''
				shop_ids = []
				for shop_id in obj_pro.shop_ids:
					shop_ids.append(shop_id.opencart_shop)
				product_data['shop_ids'] = shop_ids or [0]
				product_data['session'] = session_key
				pro = self.prodcreate(url, opencart, obj_pro, 
									product_data , instance_id , is_variants)
				ecomm_id = pro[1]
				status = True
			except Exception as e:
				error = str(e)
		return {
				'status': status,
				'ecomm_id' : ecomm_id,
				'error':error
			}
 

	def _update_opencart_specific_template(self, obj_pro_mapping, instance_id, channel, connection):
		"""
		update product template and its variants
		@param code: Obj pro, instance id , channel , connection
		@param context: A standard dictionary
		@return: Dictionary
		"""
		ctx = self._context.copy() or {}
		session_key = connection.get('session_key', False)
		opencart = connection.get('opencart',False)
		url = connection.get('url',False)
		product_configurable =  connection.get('product_configurable', False)
		status = False
		ecomm_id = False
		oc_categ_id = 0
		option_id = False
		product_data = {}
		option_val_obj = self.env['connector.option.mapping']
		option_obj = self.env['connector.attribute.mapping']
		product_connector =  self.env['connector.product.mapping']
		is_variants = False
		ecomm_product_id = obj_pro_mapping.ecomm_id
		obj_pro = obj_pro_mapping.name
		route = 'product'
		error = ''
		lang_data = False
		if obj_pro and session_key and opencart and url:
			try:
				if product_configurable =='variants':
					product_data = self.get_product_variant_data(obj_pro , instance_id)
					if 'oc_option_value_ids' in product_data:
						obj_pro_mapping.is_variants = True
						is_variants = True
					else:
						obj_pro_mapping.is_variants = False
				else:
					product_data['variant_id'] = str(
						obj_pro.product_variant_ids[0].id)
				oc_categ_id = 0
				prod_catg = []
				for j in obj_pro.connector_categ_ids.categ_ids:
					oc_categ_id = self.sync_categories(j , instance_id, channel, connection )
					prod_catg.append(oc_categ_id)
				if obj_pro.categ_id.id:
					oc_categ_id = self.sync_categories(obj_pro.categ_id, instance_id ,channel, connection)
					prod_catg.append(oc_categ_id)
				product_data['product_id'] = ecomm_product_id
				product_data['sku'] = obj_pro.default_code or 'Ref Odoo %s' % obj_pro.id
				product_data['model'] = obj_pro.default_code or 'Ref Odoo %s' % obj_pro.id
				if ctx.get('translation_sync'):
					lang_data = ctx.get('translated_values', False)
				if lang_data:
					product_data['lang_description'] = {}
					for lang_id, lang_values in lang_data.items():
						product_data['lang_description'].update({
							lang_id:{
								'name':lang_values['name'],
								'keyword': lang_values['name'],
								'description': lang_values['description'] or ' ',
								'meta_description':lang_values['meta_tag_description'] or '',
								'meta_keyword':lang_values['meta_tag_keyword'] or '',
								'meta_title':lang_values['meta_tag_title'] or '',
								'tag':lang_values['tag'] or ''
								}})
				product_data['name'] = obj_pro.name
				product_data['keyword'] = obj_pro.name
				product_data['description'] = obj_pro.oc_description or ' '
				product_data['meta_description'] = obj_pro.meta_tag_description or ' '
				product_data['meta_keyword'] = obj_pro.meta_tag_keyword or ' '
				product_data['meta_title'] = obj_pro.meta_tag_title or ' '
				product_data['tag'] = obj_pro.product_tag or ' '
				product_data['ean'] = obj_pro.barcode or ' '
				product_data['price'] = obj_pro.list_price or 0.00
				product_data['quantity'] = self.env['connector.snippet'].get_quantity(obj_pro.product_variant_ids[0], instance_id)
				product_data['weight'] = obj_pro.weight or 0.00
				product_data['erp_product_id'] = obj_pro.id
				product_data['product_category'] = list(set(prod_catg))
				product_data['erp_template_id'] = obj_pro.id
				product_data['manufacturer_id'] = self.check_specific_brand(obj_pro.product_brand_id, connection, instance_id) or ''
				product_data['product_image'] = obj_pro.image_1920
				if product_data['product_image']:
					product_data['product_image'] = product_data['product_image'].decode()
				product_data['manufacturer_id'] = self.check_specific_brand(obj_pro.product_brand_id, connection, instance_id) or ''
				shop_ids = []
				for shop_id in obj_pro.shop_ids:
					shop_ids.append(shop_id.opencart_shop)
				product_data['shop_ids'] = shop_ids or [0]
				product_data['session'] = session_key
				param = json.dumps(product_data)
				resp = opencart.get_session_key(url+route, param)
				resp = resp.json()
				key = str(resp[0])
				oc_id = resp[1]
				status = resp[2]
				if status:
					for k in oc_id['merge_data']:
						search = product_connector.search([('odoo_id', '=', int(k)),('instance_id','=',instance_id)])
						if search and is_variants:
							search = search.unlink()
						self.create_odoo_connector_mapping('connector.product.mapping', 
											ecomm_product_id, 
											int(k), 
											instance_id,
											odoo_tmpl_id = product_data['erp_template_id'],
											ecomm_option_id = int(oc_id['merge_data'][k]),
											name = int(k))

					obj_pro_mapping.need_sync = 'No'
			except Exception as e:
				error = str(e)
		return{
				'status':status,
				'error':error
			}
		  