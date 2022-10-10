
from odoo import fields, models, api


class alifzerocmsDegree(models.Model):
    _name = 'alifzerocms.degree'
    _description = 'Degree'

    name = fields.Char('Degree Name', required=True)
    code = fields.Char('Code', required=True)
    career_id = fields.Many2one('alifzerocms.career', string="Admission Career")
    sequence = fields.Integer('Sequence',default=10)
    active = fields.Boolean(default=True)

    program_ids = fields.Many2many('alifzerocms.program', 'program_degree_rel', 'degree_id', 'program_id', 'Programs')


class alifzerocmsProgram(models.Model):
    _inherit = "alifzerocms.program"

    degree_ids = fields.Many2many('alifzerocms.degree','program_degree_rel','program_id','degree_id','Degrees')

# class alifzerocmsDistrict(models.Model):
#     _name = 'alifzerocms.district'
#     _description = 'District'
#
#     province_id = fields.Many2one('alifzerocms.province', string="Province")
#     name = fields.Char('District Name',size=32, required=True)
#     code = fields.Char('Code', size=8, required=True)

