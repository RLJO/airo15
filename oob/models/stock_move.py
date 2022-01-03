#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

from odoo import api, fields, models, _
import json
import logging
_logger = logging.getLogger(__name__)

################## .............opencart-odoo stock.............##################

class StockMove(models.Model):
    _inherit="stock.move"

    def opencart_stock_update(self, erp_product_id, warehouse_id):
        ctx = self._context.copy() or {}
        qty = 0
        session = 0
        text = ''
        stock = 0
        product_pool = self.env['connector.product.mapping']
        check_mapping = product_pool.sudo().search([('name','=',erp_product_id)],limit=1)
        if check_mapping and erp_product_id:
            map_obj = check_mapping[0]
            oc_product_id = map_obj.ecomm_id
            oc_option_id = map_obj.ecomm_option_id
            instance_id = map_obj.instance_id
            if instance_id and ((instance_id.connector_stock_action == 'qoh'  and ctx['stock_operation'] == '_action_done')\
                 or (instance_id.connector_stock_action != 'qoh' and \
                      (ctx['stock_operation'] == '_action_cancel' or ctx['stock_operation'] == '_action_confirm'))) \
                          and warehouse_id == instance_id.warehouse_id.id:
                ctx.update({'instance_id':instance_id.id})
                connection = self.env['connector.instance'].sudo().with_context(ctx)._create_opencart_connection()
                if connection['status'] and instance_id.inventory_sync == 'enable':
                    ctx['warehouse'] = instance_id.warehouse_id.id
                    product_qty = self.env['connector.snippet'].with_context(ctx) \
                        .get_quantity(self.env['product.product'].browse(erp_product_id),instance_id.id)
                    url = connection.get('url', False)
                    session_key = connection.get('session_key', False)
                    opencart = connection.get('opencart' ,False)
                    if url and session_key and opencart:
                        params={}
                        route = 'UpdateProductStock'
                        params['stock'] = product_qty
                        params['product_id'] = oc_product_id
                        if oc_option_id != 0:
                            params['option_id'] = oc_option_id
                            params['option_qty'] = product_qty
                        params['session'] = session_key
                        try:
                            resp = opencart.get_session_key(url+route, params)
                            resp = resp.json()
                            key = str(resp[0])
                            status = resp[1]
                            if not status:
                                return [0,str(key)]
                            return [1, True]
                        except Exception as e:
                            return[0, 'Stock Not Updated To Opencart']
                    else:
                        return[0, 'Url Or Session Key Not Found']
        else:
            return [0,'Error in Updating Stock, Product Id %s not mapped.'%erp_product_id]
