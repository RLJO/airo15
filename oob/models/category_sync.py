# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

# Category Sync Operation

from odoo import api, models

class ConnectorSnippet(models.TransientModel):
    _inherit = "connector.snippet"

    def create_opencart_category(self ,odoo_id, parent_categ_id , name ,connection):
        """ create opencart product category from odoo
        @params : odoo category id, openerp parent categ id, category name, opencart connection dictionay
        return : dictionary 
        
        """
        session_key = connection.get('session_key', False)
        opencart = connection.get('opencart',False)
        url = connection.get('url',False)
        status = True
        ecomm_id = False
        error = ''
        if session_key and opencart and url:
            route = 'category'
            catgdetail = dict({
                'name': name,
                'erp_category_id': odoo_id
            })
            if parent_categ_id==1:
                catgdetail['parent_id'] = 0
            else:
                catgdetail['parent_id'] = parent_categ_id
            catgdetail['session'] = session_key
            try:
                resp = opencart.get_session_key(url+route, catgdetail)
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
        else:
            status = False
        return {
            'status' : status,
            'ecomm_id':ecomm_id,
            'error' : error
            }

    
    def update_opencart_category(self, vals , ecomm_id , connection):
        """ update opencart product category from odoo
        @params : vals(name, parent_id), opencart category id, opencart connection dictionay
        return : dictionary 
        
        """
        session_key = connection.get('session_key', False)
        opencart = connection.get('opencart',False)
        url = connection.get('url',False)
        status = True
        error = ''
        if session_key and opencart and url:
            get_category_data = {}
            route = 'category'
            cat = ''
            name = vals.get('name', '')
            cat_data = False
            get_category_data['category_id'] = ecomm_id
            get_category_data['session'] = session_key
            get_category_data['name'] = name
            if vals.get('parent_id'):
                if vals['parent_id']==1:
                    vals['parent_id'] = 0
                get_category_data ['parent_id'] = vals['parent_id']
            try:
                resp = opencart.get_session_key(url+route, get_category_data)
                resp = resp.json()
                key = str(resp[0])
                status = resp[1]
                if not status:
                    status = False
            except Exception as e:
                status = False
                error = str(e)
        else:
            status = False
        return {
            'status' : status,
            'error' : error
        }
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        prestashop = connection.get('prestashop', False)
        status = True
        name = vals.get('name', '')
        cat_data = False
        if vals.get('parent_id') == 1:
            parent_categ_id = 2
        else:
            parent_categ_id = vals.get('parent_id', False)
        if prestashop and name:
            try:
                cat_data = prestashop.get('categories', ecomm_id)
            except Exception as e:
                status = False
            if cat_data:
                if type(cat_data['category']['name']['language']) == list:
                    for i in range(len(cat_data['category']['name']['language'])):
                        cat_data['category']['name']['language'][i]['value'] = name
                        cat_data['category']['link_rewrite']['language'][i]['value'] = self._get_link_rewrite(zip, name)
                        cat_data['category']['description']['language'][i]['value'] = 'None'
                        cat_data['category']['meta_description']['language'][i]['value'] = 'None'
                        cat_data['category']['meta_keywords']['language'][i]['value'] = 'None'
                        cat_data['category']['meta_title']['language'][i]['value'] = name
                else:
                    cat_data['category']['name']['language']['value'] = name
                    cat_data['category']['link_rewrite']['language']['value'] = self._get_link_rewrite(zip, name)
                    cat_data['category']['description']['language']['value'] = 'None'
                    cat_data['category']['meta_description']['language']['value'] = 'None'
                    cat_data['category']['meta_keywords']['language']['value'] = 'None'
                    cat_data['category']['meta_title']['language']['value'] = name
                cat_data['category']['id_parent'] = parent_categ_id or '2'
                a1 = cat_data['category'].pop('level_depth',None)
                a2 = cat_data['category'].pop('nb_products_recursive',None)
                try:
                    ecomm_data = prestashop.edit('categories', ecomm_id, cat_data)
                except:
                    status = False
        else:
            status = False
        return {
            'status' : status,
            }

