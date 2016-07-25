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
        
        env = request.env(user=SUPERUSER_ID)
        
        value = {
            'sponsor_issponsor': False,
            'partner_state': 'state_waiting'
        }
        

        for f in ['name', 'sponsor_cvr', 
                  'street', 'zip', 'city', 'sponsor_url',
                  'sponsor_kontaktperson_name', 'sponsor_kontaktperson_mail', 'sponsor_kontaktperson_tlf',
                  'partner_bidrag_1', 'partner_bidrag_2', 'partner_bidrag_3', 'partner_bidrag_4', 'partner_bidrag_5',
                  'partner_aktivitet', 'partner_onsker', 'partner_nextsteps', 'partner_bemarkninger',
                  
                  ]:
            value[f] = post.get(f)
            
        

        part = env['model.sponsor'].create(value)
        
        
        template = part.env.ref('campos_sponsor.request_partnerconfirm')
        assert template._name == 'email.template'
        try:
            template.send_mail(part.id)
        except:
            pass
        
        
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
    
    
    
    
    
    
class activitycontroller(http.Controller):    
    signupurl = '/campos/activity/signup'
    thankyouurl = '/page/campos-activity-thankyou'
    confirmurl = '/campos/confirm/<mode>/<token>'
    
    
    @http.route('/campos/activity/signup',
        type='http', auth="public", website=True)
    def index(self, **kw):
        return request.render('campos_sponsor.activity_signup', {
        })
        
    



    @http.route('/page/campos-activity-thankyou',
        methods=['POST'], type='http', auth="public", website=True)
    def activity_thankyou(self, **post):
        
        env = request.env(user=SUPERUSER_ID)
        
        value = {
            'activity_state': 'state_waiting'
        }
        

        for f in ['activity_name', 'activity_groupname', 'activity_description', 'activity_participant_usage', 'activity_participant_knowledge',
                  'activity_contact1_name', 'activity_type', 'activity_contact1_road', 'activity_contact1_zip', 'activity_contact1_city', 'activity_contact1_email', 'activity_contact1_tlf',
                  'activity_age_from', 'activity_age_to', 'activity_expected_participants',
                  'activity_expense_total',
                  
                  ]:
            value[f] = post.get(f)
            
        

        part = env['model.activity'].create(value)
        
        return request.render("campos_sponsor.activity_thankyou", {'par':part})
    
        
        