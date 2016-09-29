# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

import odoorpc
import werkzeug
from xml.etree import ElementTree as ET
from urllib import urlopen

import logging
import traceback

_logger = logging.getLogger(__name__)

class CamposRemoteSystem(models.Model):

    _name = 'campos.remote.system'
    _description = 'Campos Remote System'  # TODO

    name = fields.Char()
    host = fields.Char()
    port = fields.Integer(default=443)
    protocol = fields.Char(default='jsonrpc+ssl')
    db_name = fields.Char('Database')
    db_user = fields.Char('User')  # System ID for BM
    db_pwd = fields.Char('Password')
    oauth_provider_id = fields.Many2one('auth.oauth.provider')
    systype = fields.Selection([('ms', 'Medlemsservice'),
                                ('bm', u'Blåt Medlem')], 'System type', default='ms')
    treasurer_function = fields.Char()
    scoutorg_id = fields.Many2one('campos.scout.org', 'Scout organization')

    @api.model
    def getRemoteSystem(self):
        if self.env.user.oauth_provider_id:
            domain = [('oauth_provider_id', '=', self.env.user.oauth_provider_id.id)]
        else:
            domain = [('systype', '=', 'bm')]
        return self.search(domain, limit=1)
    
    def getRemoteUID(self):
        if self.systype == 'bm':
            return int(self.env.user.member_number)
        else:
            return self.env.user.oauth_uid

    def getBMurl(self, service, **param):
        bmurl =  "%s/%s?system=%s&password=%s&%s" % (self.host, service, self.db_user, self.db_pwd, werkzeug.url_encode(param))
        _logger.info('BM URL: %s', bmurl)
        return bmurl  

    def getProfiles(self, remote_int_id):
        profiles = []
        member_number = False
        if self.systype == 'ms':
            msodoo = odoorpc.ODOO(self.host, protocol=self.protocol, port=self.port)
            msodoo.login(self.db_name, self.db_user, self.db_pwd)
            Partner = msodoo.env['res.partner']
            partner = Partner.browse(int(remote_int_id))
            member_number = partner.member_number
            for profile in partner.member_id.profile_ids:
                if any([func.function_type_id.leader_function or func.function_type_id.board_function for func in profile.active_functions_in_current_organization]):
                    profiles.append({'name': profile.organization_id.name,
                                     'org_int_id': profile.organization_id.partner_id.id,
                                     'org_ext_id': profile.organization_id.organization_code,
                                     'profile_id': profile.id,
                                     })
        else:
            # bm import
            grouplist = []
            member_number = remote_int_id
            rows = ET.parse(urlopen(self.getBMurl('memberships', memberNumber=remote_int_id, orgTypes='gruppe')))
            for row in rows.getroot():
                rd = dict((e.tag, e.text) for e in row)
                _logger.info("BM row: %s", rd)
                if (rd['trustLeaderType'] or rd['trustBoardGroup']) and '-' not in rd['orgCode']:
                    org = rd['orgCode']
                    if '-' in org:
                        org = org.split('-')[0]
                    if org not in grouplist:
                        profiles.append({'name': rd['orgName'],
                                         'org_int_id': int(org),
                                         'org_ext_id': org,
                                         'profile_id': member_number,
                                        })
                        grouplist.append(org)


        return member_number, profiles
    
    def getTreasurer(self, remote_org_id):
        if self.systype == 'ms':
            msodoo = odoorpc.ODOO(self.host, protocol=self.protocol, port=self.port)
            msodoo.login(self.db_name, self.db_user, self.db_pwd)
            RemoteFunc = msodoo.env['member.function']
            domain = [('organization_id', '=', remote_org_id),('function_type_id', 'ilike', self.treasurer_function)]
            remote_func = RemoteFunc.search(domain)
            _logger.info('SRCH Tres: %s %s', domain, remote_func)
            if remote_func:
                return RemoteFunc.browse(remote_func[0]).member_id.partner_id.id
            else:
                return False
        else:
            bmurl = self.getBMurl('memberships', org=remote_org_id, trustcodes=self.treasurer_function)
            _logger.info("BMURL: %s", bmurl)
            rows = ET.parse(urlopen(bmurl))
            for row in rows.getroot():
                rd = dict((e.tag, e.text) for e in row)
                _logger.info('Kassere: %s', rd['memberNumber'])
                return int(rd['memberNumber'])

    def syncPartner(self, remote_int_id=False, partner=False, is_company = False):
        
        def country_lookup(country):
            if country:
                return self.env['res.country'].search([('name', 'ilike', country)]).id
            return False
        
        if not remote_int_id and partner:
            remote_int_id = partner.remote_int_id
        if not remote_int_id:
            return
        muni_no = False
        if self.systype == 'ms':
            msodoo = odoorpc.ODOO(self.host, protocol=self.protocol, port=self.port)
            msodoo.login(self.db_name, self.db_user, self.db_pwd)
            RemotePartner = msodoo.env['res.partner']
            remote_partner = RemotePartner.browse(int(remote_int_id))
            vals = {'name': remote_partner.name,
                    'street': remote_partner.street,
                    'zip': remote_partner.zip,
                    'city': remote_partner.city,
                    'country_id': country_lookup(remote_partner.country_id.name),
                    'phone': remote_partner.phone,
                    'mobile': remote_partner.mobile,
                    'email': remote_partner.email,
                    'remote_int_id': remote_partner.id,
                    'remote_ext_id': remote_partner.member_number,
                    'is_company': is_company,
                    'remote_system_id': self.id,
                    'last_import': fields.Datetime.now(),
                    }
            if is_company:
                vals['remote_ext_id'] = remote_partner.organization_id.organization_code
                vals['remote_link_id'] = remote_partner.organization_id.id
            else:
                vals['remote_ext_id'] = remote_partner.member_number
            muni_no = remote_partner.municipality_id.number
        else:
            # bm import
            if is_company:  # Group import
                rows = ET.parse(urlopen(self.getBMurl('organizations', org=remote_int_id)))
                for row in rows.getroot():
                    rd = dict((e.tag, e.text) for e in row)
                    vals = {'name': rd['docTitle'],
                            'street': rd['addressFull'],
                            'zip': rd['organizationPostalCode'],
                            'city': rd['City'],
                            'country_id': country_lookup(rd['Country']),
                            'phone': rd['organizationPhone'],
                            'mobile': rd['organizationMobilePhone'],
                            'email': rd['organizationEMail'],
                            'website': rd['organizationWeb'],
                            'remote_int_id': remote_int_id,
                            'remote_ext_id': remote_int_id,
                            'remote_link_id': remote_int_id,
                            'is_company': is_company,
                            'remote_system_id': self.id,
                            'last_import': fields.Datetime.now(),
                            }
                    muni_no = rd['organizationKommune']
            else:
                rows = ET.parse(urlopen(self.getBMurl('members', memberNumber=remote_int_id)))
                for row in rows.getroot():
                    rd = dict((e.tag, e.text) for e in row)
                    vals = {'name': rd['docTitle'],
                            'street': rd['addressFull'],
                            'zip': rd['userPostalCode'],
                            'city': rd['City'],
                            'country_id': country_lookup(rd['Country']),
                            'phone': rd['userPrivatePhone'],
                            'mobile': rd['userMobilePhone'],
                            'email': rd['userEMail'],
                            'remote_int_id': remote_int_id,
                            'remote_ext_id': remote_int_id,
                            'remote_link_id': remote_int_id,
                            'is_company': is_company,
                            'remote_system_id': self.id,
                            'last_import': fields.Datetime.now(),
                            }
                    muni_no = rd['userKommune']
        if muni_no:
            muni = self.env['campos.municipality'].search([('number', '=', int(muni_no))])
            if muni:
                vals['municipality_id'] = muni.id
        if not partner:
            partner = self.env['res.partner'].suspend_security().create(vals)
        else:
            partner.suspend_security().write(vals)

        return partner
    
    def getBMuserData(self, member_number):
        rows = ET.parse(urlopen(self.getBMurl('members', memberNumber=member_number)))
        for row in rows.getroot():
            rd = dict((e.tag, e.text) for e in row)
            vals = {'name': rd['docTitle'],
                    'email': rd['userEMail'],
                    'login': rd['userEMail'],
                    }
            return vals

        
