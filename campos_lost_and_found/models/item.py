from openerp import models, fields

class Item(models.Model):
    _name = 'lost.item'
    name = fields.Char('Name')
    category_id = fields.Many2one('lost.category', 'Category', ondelete='restrict')
    active = fields.Boolean('Active', default=True)