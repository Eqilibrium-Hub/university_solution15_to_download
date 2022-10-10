import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class alifzerocmsSchemeLineTag(models.Model):
    _name = 'alifzerocms.scheme.line.tag'
    _description = 'Scheme Line Tag'

    name = fields.Char(string='Name', required=True, help="Scheme Line Tag")
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer('Color')
    
    
class alifzerocmsStudyScheme(models.Model):
    _name = 'alifzerocms.study.scheme'
    _description = "CMS Study Scheme"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', copy=False)
    sequence = fields.Integer('Sequence')
    scheme_date = fields.Date(string="Scheme Date")
    active = fields.Boolean('Active', default=True,
        help="If Unchecked, it will allow you to hide the Study Scheme without removing it.")
    credits = fields.Integer('Credit Hours',compute='_compute_credits',store=True)
    career_id = fields.Many2one("alifzerocms.career", string="Career", required=True)
    session_id = fields.Many2one('alifzerocms.academic.session','Academic Session')
    program_ids = fields.Many2many('alifzerocms.program','scheme_program_rel','scheme_id','program_id',string='Program', copy=True)

    batch_ids = fields.One2many('alifzerocms.batch', 'study_scheme_id', 'Batches')
    line_ids = fields.One2many('alifzerocms.study.scheme.line','study_scheme_id',string='Study Scheme', copy=True)
    stream_ids = fields.Many2many('alifzerocms.program.stream','scheme_stream_rel','scheme_id','stream_id',string='Streams', copy=True)
    scheme_type = fields.Selection([('regular', 'Regular'), ('special', 'Special'),('minor','Minor')], 'Scheme Type', default='regular')
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Study Scheme"),
    ]

    @api.depends('line_ids', 'line_ids.credits','line_ids.course_type')
    def _compute_credits(self):
        for rec in self:
            credits = 0
            for line in rec.line_ids.filtered(lambda l: l.course_type in ('compulsory','placeholder')):
                credits += line.credits
            rec.credits = credits

    def unlink(self):
        for rec in self:
            if rec.batch_ids:
                raise ValidationError(_("Study Scheme maps with Batches and can not be deleted, You only can Archive it."))
        super(alifzerocmsStudyScheme, self).unlink()

    def cron_credits(self):
        for rec in self.search([]):
            rec._compute_credits()
            
    
class alifzerocmsStudySchemeLine(models.Model):
    _name = 'alifzerocms.study.scheme.line'
    _description = 'CMS Study Scheme Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'course_id'

    study_scheme_id = fields.Many2one('alifzerocms.study.scheme', string="Study Scheme", ondelete='cascade')
    scheme_type = fields.Selection(related='study_scheme_id.scheme_type',store=True)
    career_id = fields.Many2one('alifzerocms.career','Career',related='study_scheme_id.career_id',store=True)
    semester_id = fields.Many2one('alifzerocms.semester', string="Semester", tracking=True)
    course_type = fields.Selection([
        ('compulsory','Compulsory'),
        ('elective','Elective'),
        ('placeholder','Elective Placeholder')
    ], 'Course Type',default='compulsory', tracking=True)
    tag_ids = fields.Many2many('alifzerocms.scheme.line.tag', 'scheme_line_tag_rel','scheme_line_id','tag_id','Tags', tracking=True)
    term_id = fields.Many2one('alifzerocms.academic.term',string="Term", copy=False,tracking=True)
    course_id = fields.Many2one('alifzerocms.course',string='Course', tracking=True)
    
    course_code = fields.Char('Course Code', tracking=True)
    course_name = fields.Char('Course Name', tracking=True)
    major_course = fields.Boolean('Major Course')
    self_enrollment = fields.Boolean('Self Enrollment')
    
    component_lines = fields.One2many('alifzerocms.study.scheme.line.component', 'scheme_line_id',
        compute='_compute_components',store=True, string='Course Components', readonly=False)
    credits = fields.Float('Credits',compute='_compute_credits',store=True)
    
    prereq_operator = fields.Selection([('and','AND'),('or','OR')],'Prereq Operator',default='and')
    prereq_ids = fields.Many2many('alifzerocms.course','scheme_prereq_subject_rel','scheme_line_id','subject_id',
        compute='_compute_components',store=True, string='Prerequisite Courses',copy=False, readonly=False)
    coreq_course = fields.Many2one('alifzerocms.study.scheme.line','CO-Req Course', tracking=True,compute='_compute_components',store=True, readonly=False)
    sequence = fields.Integer('Sequence')
    
    _sql_constraints = [
        ('unique_course', 'unique(study_scheme_id,course_id)', "Course already exists in Study Scheme"), ]

    def name_get(self):
        res = []
        for record in self:
            name = record.course_id.name
            if record.course_id.code:
                name = record.course_id.code + ' - ' + name
            res.append((record.id, name))
        return res
    
    def component_hook(self,component_data):
        return component_data

    @api.depends('component_lines','component_lines.weightage')
    def _compute_credits(self):
        for rec in self:
            credits = 0
            for component in rec.component_lines:
                credits += component.weightage
            rec.credits = credits

    @api.depends('course_id')
    def _compute_components(self):
        for rec in self:
            course = rec.course_id
            components = [[5]]
            for component in course.component_lines:
                component_data = {
                    'component': component.component,
                    'weightage': component.weightage,
                    'contact_hours': component.contact_hours,
                }
                component_data = rec.component_hook(component_data)
                components.append((0, 0,component_data))
                
            rec.component_lines = components
            rec.prereq_ids = [(6,0,course.prereq_ids.mapped('prereq_id').ids)]
            if course.coreq_course:
                coreq_course = rec.study_scheme_id.line_ids.filtered(lambda l: l.course_id.id == course.coreq_course.id).id
                if "NewId" in str(coreq_course):
                    coreq_course = coreq_course.origin
                rec.coreq_course = coreq_course
                
            rec.course_code = course.code
            rec.course_name = course.name
            rec.major_course = course.major_course
            rec.self_enrollment = course.self_enrollment

    @api.onchange('course_type')  # ,'tag_ids'
    def onchagene_course_type(self):
        place_holder = self.env.ref('alifzerocms.course_placeholder')
        if self.course_type == 'placeholder':
            sub_domain = [('tag_ids','in',place_holder.ids)]
        else:
            sub_domain = [('tag_ids','not in',place_holder.ids)]

        return {
            'domain': {
                'course_id': sub_domain
            },
            'value': {
                'course_id': False,
            }
        }

    # @api.depends('study_scheme_id','subject_id','academic_semester_id')
    # def _get_import_identifier(self):
    #     for rec in self:
    #         name = (rec.study_scheme_id.code or '') + '-' + (rec.academic_semester_id.code and rec.academic_semester_id.code or str(rec.semester_id.number)) + '-' + (rec.subject_id.code or '')
    #         identifier = self.env['ir.model.data'].search(
    #             [('model', '=', 'alifzerocms.study.scheme.line'), ('res_id', '=', rec.id)])
    #
    #         if identifier:
    #             identifier.module = 'PR'
    #             identifier.name = name
    #         else:
    #             data = {
    #                 'name': name,
    #                 'module': 'SS',
    #                 'model': 'alifzerocms.study.scheme.line',
    #                 'res_id': rec.id,
    #             }
    #             identifier = self.env['ir.model.data'].create(data)
    #
    #         rec.import_identifier = identifier.id
    
    @api.model
    def create(self, vals):
        if vals.get('elective', False):
            vals['semester_id'] = False
            
        semester = vals.get('semester_id', 10)
        sequence = (vals.get('sequence', 0)) % 100
        vals['sequence'] = semester * 100 + sequence
        
        return super().create(vals)
            
    def write(self, vals):
        if vals.get('elective',False):
            vals['semester_id'] = False
        
        semester = vals.get('semester_id',self.semester_id.number) or 10
        sequence = (vals.get('sequence',self.sequence) or 0) % 100
        vals['sequence'] = semester*100+sequence
        
        ret = super().write(vals)
        return ret
    
    def cron_credits(self):
        for rec in self.search([]):
            rec._compute_credits()
    
    #     # prereq = vals.get('prereq_course',False)
    #     # if prereq:
    #     #     self.course_id.prereq_course = True
    #     # else:
    #     #     scheme_subs = self.env['alifzerocms.study.scheme.line'].search([('course_id','=',self.course_id.id)])
    #     #     if scheme_subs and len(scheme_subs) == 1:
    #     #         self.course_id.prereq_course = False


class alifzerocmsStudySchemeLineComponent(models.Model):
    _name = 'alifzerocms.study.scheme.line.component'
    _description = 'CMS Scheme Line Component'
    
    scheme_line_id = fields.Many2one('alifzerocms.study.scheme.line', ondelete='cascade')
    component = fields.Selection([
        ('lab', 'Lab'),
        ('lecture', 'Lecture'),
        ('studio', 'Studio'),
    ], string='Component')
    weightage = fields.Float(string='Credit Hours', default=3.0, help="Weightage for this Course", tracking=True)
    contact_hours = fields.Float(string='Contact Hours', default=1.0, help="Contact Hours for this Course", tracking=True)

    _sql_constraints = [
        ('unique_schemeline_component', 'unique(scheme_line_id,component)', "Component already exists in Study Scheme Line"), ]

    def name_get(self):
        return [(rec.id, (rec.scheme_line_id.course_code or '') + '-' + (rec.scheme_line_id.course_name or '') + '-' + rec.component.title()) for rec in self]