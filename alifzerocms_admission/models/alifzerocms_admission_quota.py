
from odoo import fields, models, api


class alifzerocmsAdmissionAllocation(models.Model):
    _name ='alifzerocms.admission.allocation'
    _description ='CMS Admission allocation'
    
    name = fields.Char(string='Name',required=True)
    code = fields.Char(string='Code')
    career_id = fields.Many2one('alifzerocms.career','Career',required=True)
    academic_session_id = fields.Many2one('alifzerocms.academic.session','Academic Session',required=True)
    seat_ids = fields.One2many('alifzerocms.admission.allocation.line','allocation_id',string='Allocation Seats')


class alifzerocmsAdmissionAllocationLine(models.Model):
    _name ='alifzerocms.admission.allocation.line'
    _description='CMS Admission Allocation Line'
    
    program_id = fields.Many2one('alifzerocms.program',string='Program',required=True)
    seats = fields.Integer(string='No Of Seats', required=True)
    allocation_id = fields.Many2one('alifzerocms.admission.allocation',string='Allocation',required=True)
    category = fields.Selection([
        ('open_merit', 'Open Merit'),('self_finance','Self Finance'),
        ('self_sudtained','Self Sustained'),('quota','Quota')
    ])
    quota_id = fields.Many2one('alifzerocms.admission.quota','Quota')
    merit_closed_one = fields.Float(default=0, readonly=1)

    _sql_constraints = [
        ('seats_allocation_unique', 'unique(allocation_id,program_id,category,quota_id)', "Duplicate Entry of Seats Allocation!"),
    ]


class alifzerocmsAdmissionQuota(models.Model):
    _name = 'alifzerocms.admission.quota'
    _description = 'CMS Admission Quota'
    _rec_name = 'code'
    
    # name = fields.Selection([
    #     ('balochistan', 'Balochistan Rural'),('sindh','Sindh Rural'),
    #     ('GB','GB'),('ajk','AJK'),('fata','ex-FATA'),('army','Army')
    #     , ('air force', 'Air Force'),('navy','Navy'),('dae','DAE')
    # ],string='Name', required=True)
    name = fields.Char('Code', required=True)
    code = fields.Char(string='Name')
    type = fields.Selection([
        ('rural', 'Rural'),('forces', 'Forces'),('other', 'Other')
    ], string='Type', required=True)