from openerp import tools
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as controllers
from openerp.addons.website.models.website import slug
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class partnercontroller(http.Controller):    
    signupurl = '/campos/partner/signup'
    thankyouurl = '/page/campos-partner-thankyou'
    confirmurl = '/campos/confirm/<mode>/<token>'
    
    
    
    @http.route('/campos/partner/signup',
        type='http', auth="public", website=True)
    def index(self, **kw):
        return request.render('campos_sponsor.partner_signup', {
        })
        
        
    @http.route('/page/campos-partner-thankyou',
        methods=['POST'], type='http', auth="public", website=True)
    def partner_thankyou(self, **post):
        
        _logger.info("Creating environment")
        env = request.env(user=SUPERUSER_ID)
        
        
        _logger.info("Creating value")
        value = {
            'sponsor_issponsor': False
        }
        
        _logger.info("Filling value")
        for f in ['name', 'sponsor_cvr', 
                  'street', 'zip', 'city', 'sponsor_url',
                  'sponsor_kontaktperson_name', 'sponsor_kontaktperson_mail', 'sponsor_kontaktperson_tlf',
                  'partner_bidrag_1', 'partner_bidrag_2', 'partner_bidrag_3', 'partner_bidrag_4', 'partner_bidrag_5',
                  'partner_aktivitet', 'partner_onsker', 'partner_nextsteps', 'partner_bemarkninger',
                  
                  ]:
            value[f] = post.get(f)
            
        
        _logger.info("Creating sponsor object")
        part = env['model.sponsor'].create(value)
        
        
        _logger.info("Trying to send confirmation mail")
        template = part.env.ref('campos_sponsor.request_partnerconfirm')
        assert template._name == 'email.template'
        try:
            _logger.info("Sending mail...")
            template.send_mail(part.id)
            _logger.info("Mail sent!")  
        except:
            _logger.info("Mail sending failed")
            pass
        
        
        _logger.info("Rendering thankyou page")
        return request.render("campos_sponsor.partners_thankyou", {'par':part})
    
    
    
    
    
    
    @http.route(
        ['/campos/confirm/<mode>/<token>'],
         type='http', auth="public", website=True)
    def confirm_reg(self, mode=None, token=None, **kwargs):
        request = http.request
        error = {}
        default = {}
        
        if token:
            _logger.info("Token %s", token)
            par = request.env['model.sponsor'].sudo().search([('confirm_token', '=', token)])
            if len(par) == 1:
                if mode == 'reg':
                    if par.partner_state == 'state_waiting':
                        par.sudo().state = 'state_potentiel'
                    return request.render("campos_sponsor.reg_confirmed", {'par': par})
                    
        return request.render("campos_sponsor.unknown_token")
    
    
    