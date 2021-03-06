# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################
from odoo.tools.mimetypes import guess_mimetype
from odoo.http import request
from odoo.exceptions import UserError
from ast import literal_eval
from odoo.addons.http_routing.models.ir_http import slug
from odoo import models, fields, api, _
import requests
import json
import logging
import base64
_logger = logging.getLogger(__name__)
fixed_fields_layout = ['price', 'link', 'imageLink', 'salePrice']
to_remove_keys = ['CURRENCY', 'BASE_URL', 'SLUG', 'ID', 'template_id']


class GoogleMerchantShop(models.Model):
    _name = 'google.shop'
    name = fields.Char(string="Name", required=True)

    def _default_website(self):
        return self.env['website'].get_current_website()

    def _default_pricelist(self):
        return self.env['website'].get_current_website().get_current_pricelist()

    domain_input = fields.Char(string="Domain", default="[]")
    limit = fields.Integer(string="Limit", default=10)

    channel = fields.Selection([("online", "Online"), ("local", "Local")], string="Channel",
                               required=True, help="Select that wether your store is Online or Offline")
    product_selection_type = fields.Selection([('domain', 'Domain'), ('manual', 'Manual')], default="domain",
                                              string="Product Select Way", help="Select wether you want to select the product manually or with the help of domain")
    merchant_id = fields.Char(name="Merchant Id", help="Merchant Id of your merchant account",
                              related="oauth_id.merchant_id", readonly=True)

    shop_status = fields.Selection(
        [('new', 'New'), ('validate', 'Validate'), ('error', 'Error'), ('done', 'Done')], default='new')
    currency_id = fields.Many2one(
        string="Currency", store=True, related="product_pricelist_id.currency_id")
    website_id = fields.Many2one(
        'website', string="website", default=_default_website)

    oauth_id = fields.Many2one(string="Account", comodel_name="oauth2.detail", required=True,
                               help="Select the account with which you want to sync the products")
    content_language = fields.Many2one(string="Content Language", comodel_name="res.lang",
                                       required=True, help="Language in which your products will get sync on Google Shop")
    target_country = fields.Many2one(string="Target Country", comodel_name="res.country",
                                     required=True, help="Select the country in which you want to sell the products")
    product_pricelist_id = fields.Many2one(comodel_name="product.pricelist", string="Product Pricelist", required=True,
                                           help="select the pricelist according to which your product price will get selected", default=_default_pricelist)
    field_mapping_id = fields.Many2one(comodel_name="field.mappning", string="Field Mapping", domain=[
                                       ('active', '=', True)], required=True)
    product_ids_rel = fields.Many2many(comodel_name='product.product', relation='merchant_shop_product_rel', column1='google_id', column2='product_id', domain=[
                                       ("sale_ok", "=", True), ("website_published", "=", True)], string="Products")
    shop_url = fields.Char(name="Shop URL", help="Write your domain name of your website",
                           related="oauth_id.domain_uri", readonly=True)
    mapping_count = fields.Integer(
        srting="Total Mappings", compute="_mapping_count")

    def _get_product_domain(self):
        f_domain = [("sale_ok", "=", True), ("website_published", "=", True)]
        return f_domain

    def button_export_product(self):
        all_products_to_be_upload = []
        all_products_response = []
        batch_of_all_products = {}
        field_mapping_lines = self.field_mapping_id.field_mapping_line_ids
        mapped_product_details = self.env['product.mapping'].search_read(
            [('google_shop_id', '=', self.id)], ['product_id'])
        error_product_details = self.env['product.mapping'].search_read(
            [('google_shop_id', '=', self.id), ('product_status', '=', 'error')], ['product_id'])

        error_products_product_ids = [
            x.get('product_id')[0] for x in error_product_details]
        mapped_products_product_ids = [
            x.get('product_id')[0] for x in mapped_product_details]
        error_products_mapped_ids = [(x.get('id'), x.get('product_id')[
                                      0]) for x in error_product_details]

        product_ids = None
        if(self.product_selection_type == 'domain'):
            try:
                fixed_domain = self._get_product_domain(
                ) + [('id', 'not in', mapped_products_product_ids)]
                limit = self.limit-len(error_products_product_ids) if (
                    self.limit-len(error_products_product_ids)) > 0 else 0
                domain = literal_eval(self.domain_input)
                final_domain = domain + fixed_domain
                if limit == 0:
                    product_ids = []
                else:
                    product_ids = self.env["product.product"].search(
                        final_domain, limit=limit).ids
            except:
                return self.env['wk.wizard.message'].genrated_message("Enter Domain Properly", name='Message')
        else:
            product_ids = self.product_ids_rel.ids

        context = self._context.copy()
        context.update({'lang': self.content_language.code,
                       'pricelist': self.product_pricelist_id.id, 'website_id': self.website_id.id})

        ids_to_export = list(set(product_ids)-set(mapped_products_product_ids))
        product_detail = self.with_context(context).get_product_detail(
            field_mapping_lines.ids, ids=ids_to_export)
        error_product_detail = self.with_context(context).get_product_detail(
            field_mapping_lines.ids, ids=error_products_product_ids)

        error_product_shop_link = [
            (x[0], y) for x in error_products_mapped_ids for y in error_product_detail if (x[1] == y.get('id'))]

        base_url = self.shop_url or self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        for product in product_detail:
            all_products_to_be_upload.append(self.with_context(context).get_mapped_set(
                product, field_mapping_lines, base_url=base_url, operation='insert'))

        for error_product in error_product_shop_link:
            all_products_to_be_upload.append(self.with_context(context).get_mapped_set(
                error_product[1], field_mapping_lines, base_url=base_url, operation='insert'))
        if len(ids_to_export) == 0 and len(error_product_shop_link) == 0:
            self.shop_status = "done"
            message = "There is nothing to export"
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')
        else:
            self.oauth_id.button_get_token(self.oauth_id)
            total_product = 0
            done_count = 0
            total_no_of_products_to_export = len(all_products_to_be_upload)
            while total_no_of_products_to_export > 0:
                if total_no_of_products_to_export > 1000:
                    product_to_export = all_products_to_be_upload[:1000]
                    batch_of_all_products["entries"] = product_to_export
                    all_products_to_be_upload = [
                        product for product in all_products_to_be_upload if product not in product_to_export]
                    total_no_of_products_to_export = len(
                        all_products_to_be_upload)
                else:
                    batch_of_all_products["entries"] = all_products_to_be_upload
                    total_no_of_products_to_export = 0
                response = self.with_context(
                    context).call_google_insert_api(batch_of_all_products)
                call_response = response.json()
                if response.status_code == 401:
                    self.shop_status = "error"
                    message = "Account ID might had been expired so, refresh it and try again"
                    raise UserError(_(message))
                elif response.status_code == 200:
                    if 'entries' in call_response.keys():
                        all_products_response = call_response['entries']
                        for response in all_products_response:
                            total_product += 1
                            if 'kind' and 'batchID' and 'product' in response.keys():
                                self.env['product.mapping'].create({
                                    'google_shop_id': self.id,
                                    'product_id': response['batchId'],
                                    'update_status': True,
                                    'product_status': 'updated',
                                    'message': "Product is exported Successfully",
                                    'google_product_id': response['product']['id']})
                                done_count += 1
                            else:
                                self.env['product.mapping'].create({
                                    'google_shop_id': self.id,
                                    'product_id': response['batchId'],
                                    'update_status': False,
                                    'product_status': 'error',
                                    'message': response['errors']['message'],
                                    'google_product_id': None})
                    else:
                        self.shop_status = "done"
                        message = "There is nothing to export"
                        return self.env['wk.wizard.message'].genrated_message(message, name='Message')

                else:
                    self.shop_status = "error"
                    message = "There is a problem, please check field mapping and other settings..."
                    raise UserError(_(message))
            message = ("{0} out of {1} products are exported".format(
                done_count, total_product))
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')

    def button_update_product(self, update_all_product=False):
        all_products_to_be_upload = []
        all_products_response = []
        batch_of_all_products = {}
        if update_all_product:
            updated_fields = self.env['product.mapping'].search_read(
                [('google_shop_id', '=', self.id), ('product_status', '=', 'updated')], ['product_id'])
            operation_type = 'insert'
        else:
            self.oauth_id.button_get_token(self.oauth_id)
            updated_fields = self.env['product.mapping'].search_read([('google_shop_id', '=', self.id), (
                'update_status', '=', False), ('product_status', '=', 'updated')], ['product_id'])
            operation_type = 'update'

        context = self._context.copy()
        context.update({'lang': self.content_language.code,
                       'pricelist_id': self.product_pricelist_id.id, 'website_id': self.website_id.id})
        field_mapping_lines = self.field_mapping_id.field_mapping_line_ids
        updated_products_product_ids = [
            x.get('product_id')[0] for x in updated_fields]
        updated_products_mapped_ids = [
            (x.get('id'), x.get('product_id')[0]) for x in updated_fields]
        updated_product_detail = self.with_context(context).get_product_detail(
            field_mapping_lines.ids, ids=updated_products_product_ids)
        updated_product_shop_link = [
            (x[0], y) for x in updated_products_mapped_ids for y in updated_product_detail if (x[1] == y.get('id'))]
        base_url = self.shop_url or self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')

        for product in updated_product_shop_link:
            all_products_to_be_upload.append(self.with_context(context).get_mapped_set(
                product[1], field_mapping_lines, base_url=base_url, operation=operation_type))
        if len(updated_product_shop_link) == 0:
            self.shop_status = "done"
            message = "There is nothing to update"
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')
        else:
            total_product = 0
            done_count = 0
            total_no_of_products_to_update = len(all_products_to_be_upload)
            while total_no_of_products_to_update > 0:
                if total_no_of_products_to_update > 1000:
                    product_to_update = all_products_to_be_upload[:1000]
                    batch_of_all_products["entries"] = product_to_update
                    all_products_to_be_upload = [
                        product for product in all_products_to_be_upload if product not in product_to_update]
                    total_no_of_products_to_update = len(
                        all_products_to_be_upload)
                else:
                    batch_of_all_products["entries"] = all_products_to_be_upload
                    total_no_of_products_to_update = 0
                response = self.with_context(
                    context).call_google_insert_api(batch_of_all_products)
                call_response = response.json()
                if response.status_code == 401:
                    self.shop_status = "error"
                    message = "Account ID might had been expired so, refresh it and try again"
                    raise UserError(_(message))
                elif response.status_code == 200:
                    if 'entries' in call_response.keys():
                        all_products_response = call_response['entries']
                        for response in all_products_response:
                            total_product += 1
                            if 'kind' and 'batchID' and 'product' in response.keys():
                                self.env['product.mapping'].search([['google_product_id', '=', response['product']['id']]]).write({
                                    'update_status': True,
                                    'product_status': 'updated',
                                    'message': "Product id updated Successfully",
                                    'google_product_id': response['product']['id']})
                                done_count += 1
                            else:
                                self.shop_status = "error"
                                self.env['product.mapping'].search([['product_id.id', '=', response['batchId']]]).write({
                                    'update_status': False,
                                    'product_status': 'error',
                                    'message': response['errors']['message'],
                                    'google_product_id': None})
                    else:
                        self.shop_status = "done"
                        message = "There is nothing to update"
                        return self.env['wk.wizard.message'].genrated_message(message, name='Message')

                else:
                    self.shop_status = "error"
                    message = "There is a problem, please check field mapping and other settings..."
                    raise UserError(_(message))
            message = ("{0} out of {1} products are updated".format(
                done_count, total_product))
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')

    def get_product_detail(self, field_mapping_lines_ids, ids=[]):
        """
        !!!! -------- All the query that are excuted executes here only

        """

        field_mapping_model = self.env['field.mappning.line'].search_read(
            [('id', 'in', field_mapping_lines_ids), ('fixed', '=', False)], ['model_field_id'])

        field_mapping_model_ids = [
            x.get('model_field_id')[0] for x in field_mapping_model]
        field_mapping_model_name_ids = self.env['ir.model.fields'].search_read(
            [('id', 'in', field_mapping_model_ids)], ['name'])

        field_mapping_model_name = [x.get('name')
                                    for x in field_mapping_model_name_ids]
        field_mapping_model_name.append('product_tmpl_id')

        context = self._context.copy()
        context.update({'pricelist': self.product_pricelist_id.id,
                       'website_id': self.website_id.id})
        old_session = self.env['website'].get_current_pricelist().id
        request.session['website_sale_current_pl'] = self.product_pricelist_id.id
        product_detail = self.env['product.product'].with_context(
            context).search_read([('id', 'in', ids)], field_mapping_model_name)
        request.session['website_sale_current_pl'] = old_session
        return product_detail

    def call_google_insert_api(self, post_dict={}):
        if(self.oauth_id.authentication_state == 'authorize_token'):
            api_call_headers = {'Authorization': "Bearer " +
                                self.oauth_id.access_token, 'Content-Type': 'application/json'}
            api_call_response = requests.post('https://shoppingcontent.googleapis.com/content/v2.1/products/batch',
                                              headers=api_call_headers, data=json.dumps(post_dict), verify=True)
            return api_call_response

    def _get_selection_value(self, model_obj, field_name, selected_vaue):
        result = False
        selection_data = model_obj._fields.get(field_name).selection
        for key, val in selection_data:
            if key == selected_vaue:
                result = val
                break
        return result

    def get_mapped_set(self, product_detail, field_mapping_lines, base_url, operation):
        prod_temp_ref = self.env['product.template']
        if operation == 'insert':
            product_batch_data = {
                "batchId": product_detail.get('id'),
                "merchantId": self.merchant_id,
                "method": "insert",
                "product": {
                }
            }
        else:
            product_batch_data = {
                "batchId": product_detail.get('id'),
                "merchantId": self.merchant_id,
                "method": "update",
                "productId": (self.env['product.mapping'].search([['product_id.id', '=', product_detail.get('id')]])).google_product_id,
                "product": {
                }
            }
        product_batch_data['product']['ID'] = str(product_detail.get('id'))
        product_id = self.env['product.product'].sudo().browse(
            [int(product_batch_data['product']['ID'])])
        product_batch_data['product']['template_id'] = str(
            product_id.product_tmpl_id.id)
        product_batch_data['product']['BASE_URL'] = base_url
        product_batch_data['product']['SLUG'] = slug(prod_temp_ref.search(
            [('id', '=', int(product_batch_data['product']['template_id']))], limit=1))
        product_batch_data['product']['CURRENCY'] = self.currency_id.name
        product_batch_data['product']['targetCountry'] = self.target_country.code
        product_batch_data['product']['channel'] = self.channel
        product_batch_data['product']['contentLanguage'] = self.content_language.iso_code.split("_")[
            0]
        for line in field_mapping_lines:
            key = line.google_field_id.name
            if line.fixed:
                value = line.fixed_text
            else:
                if (key in fixed_fields_layout):  # ---------------make value accorrding to fixed layout
                    v_name = product_detail.get(
                        line.model_field_id.name) or line.default
                    value = self.default_designed_function(
                        key, v_name, product_batch_data['product'])
                else:
                    value = product_detail.get(line.model_field_id.name)
                    if line.model_field_id.ttype in ["selection"]:
                        value = self._get_selection_value(
                            prod_temp_ref, line.model_field_id.name, product_detail.get(line.model_field_id.name))
                    value = value or line.default
            if value:
                product_batch_data['product'][key] = value

        for key in to_remove_keys:
            if(key in product_batch_data['product'].keys()):
                product_batch_data['product'].pop(key)
        if operation == 'update':
            # because update not allow these parameters
            if 'id' in product_batch_data['product'].keys():
                product_batch_data['product'].pop('id')
            if 'offerId' in product_batch_data['product'].keys():
                product_batch_data['product'].pop('offerId')
            if 'targetCountry' in product_batch_data['product'].keys():
                product_batch_data['product'].pop('targetCountry')
            if 'channel' in product_batch_data['product'].keys():
                product_batch_data['product'].pop('channel')
            if 'contentLanguage' in product_batch_data['product'].keys():
                product_batch_data['product'].pop('contentLanguage')
        return product_batch_data

    def default_designed_function(self, key, value, d):
        product = self.env['product.product'].search([('id', '=', d['ID'])])
        if(key == 'price'):
            pricelist = self.env['product.pricelist'].search(
                [('name', '=', d['CURRENCY'])], limit=1)
            price_info = product._get_combination_info_variant(
                pricelist=pricelist)
            return dict(
                value=price_info.get('price'),
                currency=d.get('CURRENCY')
            )
        elif (key == 'link'):
            product_url = d.get('BASE_URL')+"/shop/product/"+d.get('SLUG')

            return product_url
        elif (key == 'imageLink'):
            image_url = "%s/web/image/product.product/%s/image_1920/%s.%s" % (d.get('BASE_URL'), d.get(
                'ID'), d.get('SLUG'), (guess_mimetype(base64.b64decode(product.image_1920))).split('/')[1])

            return image_url
        elif (key == 'salePrice'):
            pricelist = self.env['product.pricelist'].search(
                [('name', '=', d['CURRENCY'])], limit=1)
            price_info = product._get_combination_info_variant(
                pricelist=pricelist)
            return dict(
                value=price_info.get('list_price'),
                currency=d.get('CURRENCY')
            )
        else:
            pass

    def button_authorize_merchant(self):
        if self.merchant_id:
            api_call_response = {}
            self.oauth_id.button_get_token(self.oauth_id)
            try:
                api_call_headers = {
                    'Authorization': "Bearer "+self.oauth_id.access_token}
                api_call_response = requests.get('https://www.googleapis.com/content/v2.1/'+self.merchant_id +
                                                 '/accounts/'+self.merchant_id, headers=api_call_headers, verify=False)
                _logger.debug(
                    "Resopnse status of the Autn Token and Merchan ID :- %r", api_call_response.status_code)
            except:
                message = "Please Go to Account in setting and generate account token first"
                return self.env['wk.wizard.message'].genrated_message(message, name='Message')
            response_dict = json.loads(api_call_response.text)
            if api_call_response.status_code == 401:
                message = "Account ID might had been expired so, refresh it and try again or Check your Merchant ID"
                return self.env['wk.wizard.message'].genrated_message(message, name='Message')
            elif api_call_response.status_code != 200:
                message = "Error: "+response_dict.get('error').get('message')
                return self.env['wk.wizard.message'].genrated_message(message, name='Message')
            else:
                self.shop_status = 'validate'
        else:
            raise UserError(
                "Please enter the merchant ID in the account Section first")

    def _criteria(self):
        same_record = self.search(
            ['&', '&',
                ('channel', '=', self.channel),
                ('target_country', '=', self.target_country.id),
                ('content_language', '=', self.content_language.id)
             ]
        ).ids

        if len(same_record) > 1:
            return False
        return True

    _constraints = [
        (_criteria, 'Same Shop Exists in Database', [
         'channel', 'target_country', 'content_language'])
    ]

    def unlink(self):

        if self.mapping_count <= 0:
            return super(GoogleMerchantShop, self).unlink()
        else:
            raise UserError(
                "Firstly Delete all the mappings then the shop will be deleted")

    def test_function(self):

        mappings = self.env['product.mapping'].search(
            [('google_shop_id', '=', self.id)]).ids
        action = self.env.ref(
            'google_shop.product_mapping_action_button_click').read()[0]
        action['domain'] = [('id', 'in', mappings)]
        return action

    def _mapping_count(self):
        self.mapping_count = self.env['product.mapping'].search_count(
            [('google_shop_id', '=', self.id)])

    def button_delete_product_link(self):
        oauth2_error, error_count, done_count = 0, 0, 0
        mapping_ref = self.env['product.mapping'].search(
            [('google_shop_id', '=', self.id)])
        self.oauth_id.button_get_token(self.oauth_id)
        oauth_token = self.oauth_id.access_token
        merchant_id = self.merchant_id
        for i in mapping_ref:
            response = i.delete_mapping(
                oauth_token=oauth_token, merchant_id=merchant_id)
            if response == "3":
                oauth2_error = 1
                break
            elif response == "2":
                error_count += 1
            elif response == "1":
                done_count += 1
            else:
                self.shop_status = "error"
                message = response
                return self.env['wk.wizard.message'].genrated_message(message, name='Message')

        if oauth2_error > 0:
            self.shop_status = "error"
            message = "Account ID might had been expired so, refresh it and try again"
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')
        elif error_count > 0 or done_count > 0:
            total_product = done_count+error_count
            if error_count > 0:
                self.shop_status = "error"
            else:
                self.shop_status = "new"
            message = ("{0} out of {1} products are deleted".format(
                done_count, total_product))
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')
        elif len(mapping_ref) == 0:
            self.shop_status = "done"
            message = "There is nothing to delete"
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')
