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


class webtourcontroller(http.Controller):    
    departureurl = '/campos/webtour/departure'
    thankyouurl = '/page/campos-departure-thankyou'
    #confirmurl = '/campos/confirm/<mode>/<token>'


    @http.route(['/campos/webtour/departure',],
        type='http', auth="user", website=True)
    def index(self, **kw):
        return request.render('campos_transportation.webtour_departure', {})
        
            
    @http.route('/page/campos-departure-thankyou',
        methods=['POST'], type='http', auth="public", website=True)
    def departure_thankyou(self, **post):
        
        env = request.env(user=SUPERUSER_ID)
        
        value = {}
        
        for f in ['bsidno', 'pax',]:
            value[f] = post.get(f)
            
        
        bus = env['campos.webtour.bus'].create(value)
        
        '''
        template = part.env.ref('campos_transportation.request_webtourconfirm')
        assert template._name == 'email.template'
        try:
            template.send_mail(part.id)
        except:
            pass
        '''
        return request.render('campos_transportation.webtour_departure', {})
