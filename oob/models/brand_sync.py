# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

# Attribute Sync Operation

from odoo import api, models
import logging
_logger = logging.getLogger(__name__)

class ConnectorSnippet(models.TransientModel):
	_inherit = "connector.snippet"

	def export_brands(self):

		""" create opencart product attribute from odoo
		@params : attribute name, attribute id, opencart connection dictionay, ecommerce attribute code
		return : dictionary 
		
		"""
		ctx = self._context.copy() or {}
		instance_id = ctx.get('instance_id', False)
		connection = False
		connector_brand = self.env['connector.brand.mapping']
		core_brand = self.env['wk.product.brand']
		success_ids = []
		unsuccess_ids = []
		message = ''
		if instance_id:
			connection = self.env['connector.instance']._create_opencart_connection()
		if connection:
			session_key = connection.get('session_key', False)
			opencart = connection.get('opencart',False)
			url = connection.get('url',False)
			status = True
			if session_key and opencart and url:
				route = 'manufacturer'
				exported_ids = connector_brand.search([('instance_id','=', instance_id)]).mapped('name').ids
				to_export_ids = core_brand.search([('id','not in', exported_ids)])
				if to_export_ids:
					for brand_id in to_export_ids:
						brandDetail = dict({
						'name': brand_id.name,
						'odoo_id': brand_id.id,
						'sort_order' : brand_id.sequence or '0'
						})
						if brand_id.image:
							brandDetail['image'] = brand_id.image.decode() or ''
						brandDetail['session'] = session_key
						try:
							resp = opencart.get_session_key(url+route, brandDetail)
							resp = resp.json()
							key = str(resp[0])
							oc_id = resp[1]
							status = resp[2]
							if status:
								ecomm_id = oc_id
							else:
								status = False
						except Exception as e:
							status = False
							error = str(e)
						if status:
							self.create_odoo_connector_mapping('connector.brand.mapping', 
											ecomm_id, 
											brand_id.id, 
											instance_id,
											name = brand_id.id
											)
							success_ids.append(brand_id.id)
						else:
							unsuccess_ids.append(brand_id.id)
		if not unsuccess_ids:
			message = 'All Brands Are SuccessFully Exported'
		elif unsuccess_ids or success_ids:
			message = 'Successfully Exported Brands={} and Unsuccessfully Exported Brands{}'.format(success_ids, unsuccess_ids)
		else:
			message = 'Nothing Exported(Error Appears Kindly contact the module primary team)'
		return self.env['message.wizard'].genrated_message(message)
	

	def check_specific_brand(self, brand_id, connection, instance_id):
		session_key = connection.get('session_key', False)
		opencart = connection.get('opencart',False)
		url = connection.get('url',False)
		connector_brand = self.env['connector.brand.mapping']
		ecomm_id = False
		status = False
		if session_key and opencart and url and brand_id:
			route = 'manufacturer'
			search_brand = connector_brand.search([('name','=',brand_id.id),('instance_id','=', instance_id)])
			if not search_brand:
				brandDetail = dict({
				'name': brand_id.name,
				'odoo_id': brand_id.id,
				'sort_order' : brand_id.sequence or '0'
				})
				if brand_id.image:
					brandDetail['image'] = brand_id.image.decode() or ''
				brandDetail['session'] = session_key
				try:
					resp = opencart.get_session_key(url+route, brandDetail)
					resp = resp.json()
					key = str(resp[0])
					oc_id = resp[1]
					status = resp[2]
					if status:
						ecomm_id = oc_id
					else:
						status = False
				except Exception as e:
					status = False
			else:
				ecomm_id = search_brand.ecomm_id
				   
			if status:
				self.create_odoo_connector_mapping('connector.brand.mapping', 
								ecomm_id, 
								brand_id.id, 
								instance_id,
								name = brand_id.id
								)
		return ecomm_id
						  
													