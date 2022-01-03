# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

############## Overide Core classes for maintaining OpenCart Information #################


from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools.translate import _
import json
from . import oobapi
from .oobapi import OpencartWebService, OpencartWebServiceDict

API_PATH = 'index.php?route=api/oob/'
class ConnectorInstance(models.Model):
    _inherit = 'connector.instance'

    session_key  = fields.Char('Opencart Api Token' , readonly = True)
    pwd  = fields.Text('Opencart Api Key')
    product_configurable = fields.Selection([('template','Product Template'),('variants','Product Variants')], default = 'template')


    @api.model
    def create(self, vals):
        if 'pwd' in vals:
            vals['pwd']=vals['pwd'].strip()
        if 'user' in vals:
            if not vals['user'].endswith('/'):
                vals['user'] += '/'
        return super(ConnectorInstance, self).create(vals)
	
    
    def write(self, vals):
        if 'pwd' in vals:
            vals['pwd']=vals['pwd'].strip()
        if 'user' in vals:
            if not vals['user'].endswith('/'):
                vals['user'] += '/'
        return super(ConnectorInstance, self).write(vals)
	
    
    def test_opencart_connection(self):
        """
            test connection from odoo to opencart
            @params:self
            returns: wizard
        """
        text = 'Test connection Un-successful please check the opencart api credentials!!!'
        status = 'OpenCart Connection Un-successful'
        param = {}
        route = 'login'
        session = ''
        url = self.user + API_PATH
        param['api_key'] = self.pwd
        opencart = OpencartWebServiceDict()
        try:
            resp = opencart.get_session_key(url+route, param)
            status_code = resp.status_code
            if status_code in [200, 201]:
                resp = resp.json()
                if isinstance(resp, list) and resp[1]:
                    key = str(resp[0])
                    status = resp[1]
                    if status:
                        self.write({'session_key':key})
                        text = 'Test Connection with opencart is successful, now you can proceed with synchronization.'
                        status = "Congratulation, It's Successfully Connected with OpenCart Api."
                        self.status = status
                        self.connection_status = True
                    else:
                        text += '\n %r'%key
                        self.connection_status = False
                else:
                    self.status = status
                    self.session_key = False
                    self.connection_status = False
                    text = "%r \n%r \n"%(status_code, text)
                    if 'error' in resp:
                        text += resp['error']['ip']+'\n' + resp['error']['key']
        except Exception as e:
            text = text + str(e)
        return self.env['message.wizard'].genrated_message(text)
            



    
    def _create_opencart_connection(self):
        """
            create opencart connection from odoo to opencart
            @params:self
            returns: dictionary
        """
        status = False
        instance_id = self._context.get('instance_id', False)
        opencart = False
        session_key = False
        url = False
        product_configurable = 'template'
        if instance_id:
            instance_id = self.browse(instance_id)
            opencart = OpencartWebServiceDict()
            status = True
            url = instance_id.user + API_PATH
            session_key = instance_id.session_key
            product_configurable = instance_id.product_configurable
        return {
            'status' : status,
            'opencart' : opencart,
            'url' : url,
            'session_key': session_key,
            'product_configurable': product_configurable
        }        
        