# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields

import logging
_logger = logging.getLogger(__name__)

class CamposCampArea(geo_model.GeoModel):
    _description = 'Camp Area'
    _name = 'campos.camp.area'
    
    name = fields.Char('Name', size=64)
    code = fields.Char('Code', size=16)
    desc = fields.Text('Description')
    max_cap = fields.Integer('Max')
    event_id = fields.Many2one('event.event', 'Event')
    reg_ids = fields.One2many('event.registration', 'camp_area_id', 'Troops')
    reg_view_ids = fields.One2many('campos.registration.view', 'camp_area_id', 'Troops')
    addreg_id = fields.Many2one('event.registration', 'Add Registration', ondelete='set null', domain=[('state','!=', 'cancel')])
    allocated = fields.Integer('Allocated', compute="_compute_allocated")
    subcamp_id = fields.Many2one('campos.subcamp', 'Sub Camp')
    the_geom = geo_fields.GeoMultiPolygon('NPA Shape')
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='cascade')
    part_function_ids = fields.One2many(related='committee_id.part_function_ids', string='Coordinators')
    
    mailgroup_id = fields.Many2one('mail.group',
                                   'Mail list',
                                   ondelete='cascade')

    
    @api.one
    @api.depends('reg_ids')
    def _compute_allocated(self):
        self.allocated = len(self.reg_ids)

    @api.one
    def _create_committee(self):
        if not self.committee_id:
            parent = self.env['campos.committee'].search([('name', '=', self.subcamp_id.name), ('parent_id', '=', self.env.ref('campos_event.camp_area_committee').id)])
            if not parent:
                parent = self.env['campos.committee'].create({'name': self.subcamp_id.name,
                                                              'parent_id' : self.env.ref('campos_event.camp_area_committee').id
                                                              }
                                                             )
            self.committee_id = self.env['campos.committee'].create({'name': self.name,
                                                                     'code': self.code,
                                                                     'parent_id': parent.id,
                                                                     })
        if not self.mailgroup_id:
            self.mailgroup_id = self.env['mail.group'].with_context(mail_create_nosubscribe=True).create({'name': "Kvarter %s / %s" % (self.name, self.subcamp_id.name),
                                                                'alias_name': "kvarter-%s" % (self.code),
                                                                })