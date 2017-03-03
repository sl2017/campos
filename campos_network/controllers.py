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

class networkcontroller(http.Controller):
    
    @http.route('/campos/network/register',
        type='http', auth="public", website=True)
    def index(self, **kw):
        return request.render('campos_network.network_registration', {
        })
        