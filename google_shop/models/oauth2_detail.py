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
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.http import request
import requests
import json
import logging
_logger = logging.getLogger(__name__)


class Detail_oauth2(models.Model):
    _name = 'oauth2.detail'
    sequence_no = fields.Integer(string="Sequence No", required=True,
                                 help="Enter sequence no you want to add in your callback url")
    name = fields.Char(string="Token Name", required=True,
                       help="Enter name to your OAuth 2.0")
    email = fields.Char(string="Admin Email",
                        help="Admin Email address", compute="_default_configuration_calculate")
    account_token_page_url = fields.Char(string="Token page url",
                                         help="Token page view url send to user in mail", compute="_compute_token_page_url")
    authorize_url = fields.Char(
        string="Authorize URL", default="https://accounts.google.com/o/oauth2/auth", readonly=True)
    token_url = fields.Char(
        string="Token URL", default="https://accounts.google.com/o/oauth2/token", readonly=True)
    domain_uri = fields.Char(string="Shop URL", required=True,
                             help="Domain where You what google to authenticate")
    callback_uri = fields.Char(string="Callback URL", required=True,
                               help="URL where You what google to authenticate", compute="_comute_callback")
    client_id = fields.Char(
        string="Client Id", required=True, help="OAuth 2.0 Client Id")
    client_secret = fields.Char(
        string="Client Secret", required=True, help="OAuth 2.0 Client Secret Id")
    authorization_redirect_url = fields.Char(
        string="Authorization Redirect Url", readonly=True)
    authorization_code = fields.Char(string="Authorization Code")

    # =========================================================================================================================
    config_merchant_detail = fields.Boolean(
        "Configure Merchant Detail", default=False)
    verify_account_url = fields.Char(
        string="URL to Verify", help="URL to verify your Website")
    verify_url_data = fields.Text(
        string="Data in URL", help="Data in your URL")
    merchant_id = fields.Char(string="Merchant ID",
                              help="ID of the Merchant Account")
    # =========================================================================================================================
    access_token = fields.Text(string="Access Token", readonly=True)
    refresh_token = fields.Char(
        string="Refresh Token", readonly=True)
    authentication_state = fields.Selection([('new', 'New'), ('authorize_code', 'Authorize Code'), (
        'error', 'Error'), ('authorize_token', 'Access Token')], default='new')
    _sql_constraints = [
        ('sequence_no_unique', 'unique(sequence_no)', 'Sequence No should be Unique'), ('name_unique', 'unique(name)', 'Token Name should be Unique')]

    def _default_configuration_calculate(self):
        for record in self:
            record.email = self.env['res.config.settings'].get_values()[
                'admin_email']

    def button_authorize_url(self):
        self.authorization_redirect_url = self.authorize_url + '?response_type=code&client_id=' + self.client_id + \
            '&redirect_uri=' + self.callback_uri + \
            '&scope=https://www.googleapis.com/auth/content' + \
            '&access_type=offline'+'&prompt=consent'
        self.authentication_state = 'authorize_code'
        return {
            'type': 'ir.actions.act_url',
            'url': self.authorization_redirect_url,
            'target': '_new',  # open in a new tab
        }

    def _compute_token_page_url(self):
        for page in self:
            page.account_token_page_url = request.httprequest.host_url+"web#id="+str(page.id)+"&action="+str(
                page.env.ref("google_shop.oauth2_detail_action").id)+"&model=oauth2.detail&view_type=form"

    def button_get_token(self, account_id=''):
        if account_id:
            account_tokens = account_id
        else:
            account_tokens = self.env['oauth2.detail'].search([])

        template_id = self.env.ref(
            'google_shop.google_shop_mail_template')
        for token in account_tokens:
            if token.refresh_token:
                data = {'grant_type': 'refresh_token',
                        'refresh_token': token.refresh_token, 'redirect_uri': token.callback_uri}

                resp = requests.post(token.token_url, data=data, auth=(
                    token.client_id, token.client_secret))

                resp = json.loads(resp.text)

                if resp.get('access_token'):
                    try:
                        token.access_token = resp.get('access_token')
                        token.authentication_state = 'authorize_token'
                        if not account_id:
                            connected_accounts = self.env['google.shop'].search(
                                [['shop_status', '!=', 'new']]).filtered(lambda r: r.oauth_id == token)
                            if connected_accounts:
                                for account in connected_accounts:
                                    account.button_update_product(
                                        update_all_product=True)
                    except:
                        token.access_token = None
                        token.authentication_state = 'error'
                        template_id.send_mail(token.id, force_send=True)
                else:
                    token.access_token = None
                    token.refresh_token = None
                    token.authentication_state = 'error'
                    template_id.send_mail(token.id, force_send=True)

    def button_get_code(self):
        message = ""
        data = {'grant_type': 'authorization_code',
                'code': self.authorization_code, 'redirect_uri': self.callback_uri}
        resp = requests.post(self.token_url, data=data, verify=False,
                             allow_redirects=True, auth=(self.client_id, self.client_secret))
        resp = json.loads(resp.text)
        if resp.get('access_token') and resp.get('refresh_token'):
            try:
                self.access_token = resp.get('access_token')
                self.refresh_token = resp.get('refresh_token')
                self.authentication_state = 'authorize_token'
                message = "Completed"
            except:
                self.access_token = None
                self.refresh_token = None
                self.authentication_state = 'error'
                message = str(resp.get('error'))
        else:
            self.access_token = None
            self.refresh_token = None
            self.authentication_state = 'error'
            message = "No Data in Authentication Token, Please Check the Entered Detail and Try again"
        return message

    @api.onchange('domain_uri', 'sequence_no')
    def _comute_callback(self):
        for domain_sequence in self:
            if domain_sequence.domain_uri and domain_sequence.sequence_no:
                domain_sequence.callback_uri = domain_sequence.domain_uri + \
                    "/google/"+str(domain_sequence.sequence_no)+"/OAuth2"
