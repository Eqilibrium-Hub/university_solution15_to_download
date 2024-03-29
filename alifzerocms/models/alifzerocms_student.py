from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging
import re
import pdb
import sys
import ftplib
import os
import time
import base64
import codecs
from datetime import datetime, date

# _logger = logging.getLogger(__name__)


class alifzerocmsStudentTagCategory(models.Model):
    _name = 'alifzerocms.student.tag.category'
    _description = 'Student Tag Category'

    name = fields.Char(string="Category Tag", required=True)
    code = fields.Char('Category Code')
    multiple = fields.Boolean(string='Is multiple?')
    

class alifzerocmsStudentTag(models.Model):
    _name = 'alifzerocms.student.tag'
    _description = 'Student Tag'

    name = fields.Char(string="Student Tag", required=True)
    code = fields.Char('Tag Code')
    color = fields.Integer(string='Color Index')
    category_id = fields.Many2one('alifzerocms.student.tag.category',  string='Category')
    category_code = fields.Char(related='category_id.code', store=True)
    student_ids = fields.Many2many('alifzerocms.student',  string='Students')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

    
class alifzerocmsStudent(models.Model):
    _name = 'alifzerocms.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _order = 'code, id_number'
   

    @api.depends('first_name','last_name')
    def _get_student_name(self):
        for student in self:
            student.name = (student.first_name or '') + ' ' + (student.last_name or '')

    first_name = fields.Char('First Name', required=True, tracking=True)
    last_name = fields.Char('Last Name', tracking=True)
    
    father_name = fields.Char(string="Father Name", tracking=True)
    father_status = fields.Selection([('alive','Alive'),('deceased','Deceased')],'Father Status',default='alive')
    father_profession = fields.Many2one('alifzerocms.profs','Father Profession')
    father_income = fields.Integer('Father Income')
    father_cell = fields.Char('Father Cell')
    #
    mother_name = fields.Char(string="Mother Name", tracking=True)
    mother_status = fields.Selection([('alive', 'Alive'), ('deceased', 'Deceased')], 'Mother Status', default='alive')
    mother_profession = fields.Many2one('alifzerocms.profs', 'Mother Profession')
    mother_income = fields.Integer('Mother Income')
    mother_cell = fields.Char('Mother Cell')

    first_generation_studying = fields.Boolean('First_Generation_Studying',default=False)
    cnic = fields.Char('CNIC', size=15, tracking=True)
    cnic_expiry_date = fields.Date('CNIC Expiry Date')

    disability = fields.Boolean('Disability',default=False)
    disability_detail  = fields.Char('Disability Detail')

    passport_expiry_date = fields.Date('Passport Expiry Date',tracking=True)
    passport_no = fields.Char('Passport Number',tracking=True)
    passport_issue_date = fields.Date("Passport Issue Date")

    u_id_no = fields.Char("U.I.D")
    visa_info = fields.Char('Visa Info')
    visa_issue_date = fields.Date("Visa Issue Date")
    visa_expiry_date = fields.Date('Visa Expiry Date',tracking=True)
    domicile_id = fields.Many2one('alifzerocms.domicile','Domicile',tracking=True)

    date_of_birth = fields.Date('Birth Date', required=True, tracking=True,
        default=lambda self: self.compute_previous_year_date(fields.Date.context_today(self)))
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], 'Gender', required=True, tracking=True)
    # marital_status = fields.Many2one('alifzerocms.marital.status','Marital Status',tracking=True)
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group', tracking=True)
    religion_id = fields.Many2one('alifzerocms.religion', string="Religion", tracking=True)
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict', tracking=True)
    nationality_name = fields.Char(related = 'nationality.name', store = True)

    net_stream = fields.Selection([('Open','open'),('SATN','SATN'),('SATI','SATI')],'NET Stream')
    inter_stream = fields.Selection([('A Level','OA'),('FSc.','FSC'),('Diploma','diploma')],'Intermediate Stream')
    pbnet_cbnet = fields.Selection([('PBNET','pbnet'),('CBNET','cbnet')],'PBNET/CBNET')

    admission_no = fields.Char(string="Admission Number", readonly=True)
    id_number = fields.Char('Student ID', size=64, tracking=True)
    entryID = fields.Char('Entry ID', size=64, tracking=True)
    code = fields.Char(compute='_get_code',store=True, tracking=True)
    merit_no = fields.Char('Merit No.')
    urban_rural = fields.Selection([('urban','Urban'),('rural','Rural')],'Urban/Rural')
    pc_cadet = fields.Boolean('PC Cadet',defaul=False)

    emergency_contact = fields.Char('Emergency Contact', tracking=True)
    emergency_mobile = fields.Char('Emergency Mobile', tracking=True)
    emergency_email = fields.Char('Emergency Email', tracking=True)
    emergency_address = fields.Char('Em. Address', tracking=True)
    emergency_city = fields.Char('Em. Street', tracking=True)

    company_id = fields.Many2one('res.company', string='Company')

    is_same_address = fields.Boolean(string="Is same Address?", tracking=True)
    per_street = fields.Char()
    per_street2 = fields.Char()
    per_city = fields.Char()
    per_zip = fields.Char(change_default=True)
    per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
        domain="[('country_id', '=?', per_country_id)]")
    per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict')

    guardian_name = fields.Char('Guardian Name')
    guardian_mobile = fields.Char('Guardian Mobile')

    tag_ids = fields.Many2many('alifzerocms.student.tag', 'student_tag_rel','student_id', 'tag_id', string='Group/Tag')

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete="cascade")

    career_id = fields.Many2one('alifzerocms.career','Career', readonly=True, states={'draft': [('readonly', False)]})
    program_id = fields.Many2one('alifzerocms.program','Academic Program', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('alifzerocms.department', string="Department",related='program_id.department_id',store=True)
    institute_id = fields.Many2one('alifzerocms.institute', 'Institute',related='program_id.institute_id',store=True)
    discipline_id = fields.Many2one('alifzerocms.discipline','Discipline')
    campus_id = fields.Many2one('alifzerocms.campus','Campus',related='institute_id.campus_id',store=True)

    campus_code = fields.Char(string='Campus Code',related='campus_id.code',store=True)
    institute_code = fields.Char(string='Institute Code',related='institute_id.code',store=True)
    department_code = fields.Char(string='Department Code',related='department_id.code',store=True)
    program_code = fields.Char(string='Program Code',related='program_id.code',store=True)
    career_code = fields.Char(string='Caeeer Code',related='career_id.code',store=True)

    batch_id = fields.Many2one('alifzerocms.batch', 'Program Batch', tracking=True, readonly=True,
        states={'draft': [('readonly', False)]})
    study_scheme_id = fields.Many2one('alifzerocms.study.scheme','Study Scheme',compute='_get_study_scheme',store=True)
    minor_scheme_id = fields.Many2one('alifzerocms.study.scheme','Minor Scheme', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    term_id = fields.Many2one('alifzerocms.academic.term','Current Academic Term', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    session_id = fields.Many2one('alifzerocms.academic.session','Academic Session', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    academic_ids = fields.One2many('alifzerocms.student.academic', 'student_id', 'Academics')
    stream_id = fields.Many2one('alifzerocms.program.stream','Stream')
    semester_id = fields.Many2one('alifzerocms.semester', 'Semester')
    is_military = fields.Boolean('Is Military', related='campus_id.is_military',help='Student at Military Institute',store=True)

    new_id_number = fields.Char('New Student ID', size=64)
    #
    award_ids = fields.One2many('alifzerocms.award', 'student_id', 'Honor/Awards')
    publication_ids = fields.One2many('alifzerocms.publication', 'student_id', 'Publications')

    language_ids = fields.Many2many('alifzerocms.language', string='Languages')

    extra_activity_ids = fields.One2many('alifzerocms.extra.activity', 'student_id', 'Extra Activities')

    state = fields.Selection([
        ('draft', 'Draft'), ('enroll', 'Admitted'), ('alumni', 'Alumni'),('suspend', 'Suspend'),('struck', 'Struck Off'),
        ('defer','Deferred'), ('cancel', 'Cancel'),
        ], 'Status', default='draft', tracking=True)
    #
    # # import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier',
    # #     store=True)
    #
    _sql_constraints = [
        ('admission_no', 'unique(admission_no)', "Another Student already exists with this Admission number!"),
        ('code', 'unique(code,career_id)', "Another Student already exists with this Student ID and Career!"),
    ]

    def name_get(self):
        res = []
        for record in self:
            name = record.code + ' - ' + record.name
            res.append((record.id, name))
        return res

    @api.depends('id_number','entryID')
    def _get_code(self):
        for rec in self:
            rec.code = rec.id_number or rec.entryID or ('ST.'+str(rec.id))

    def get_student_id(self):
        if self.batch_id and self.batch_id.sequence_id:
            self.id_number = self.batch_id.sequence_id.next_by_id()

    # session_id = fields.Char()
    @api.depends('program_id','session_id','batch_id')
    def _get_study_scheme(self):
        for rec in self:
            if rec.program_id and rec.session_id and rec.batch_id:
                rec.study_scheme_id = rec.batch_id.study_scheme_id.id

                # study_schemes = self.env['alifzerocms.study.scheme'].search(
                #     [('session_id', '=', rec.session_id.id)])
                # # , ('program_ids', 'in', rec.program_id.ids)
                # for study_scheme in study_schemes:
                #     if rec.program_id.id in study_scheme.program_ids.ids:
                #         rec.study_scheme_id = study_scheme.id
                #         break

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(alifzerocmsStudent, self).name_search(name, args=args, operator=operator, limit=limit)

    section_id = fields.Char()
    @api.model
    def create(self, vals):
        if vals.get('first_name',False) or vals.get('last_name',False):
            first_name = vals.get('first_name','')
            if first_name:
                first_name = first_name.title()  # capitalize
                vals['first_name'] = first_name

            name = first_name

            last_name = vals.get('last_name','')
            if last_name:
                last_name = last_name.title()  # capitalize
                vals['last_name'] = last_name
                name = name + ' ' + last_name

            vals['name'] = name

        student = super().create(vals)
        if not student.section_id:
            if student.batch_id and len(student.batch_id.section_ids) == 1:
                student.section_id = student.batch_id.section_ids[0].id
        return student

    def write(self, vals):
        auto = vals.get('auto',False)
        if auto:
            del vals['auto']
        if vals.get('first_name', False) or vals.get('last_name', False):
            first_name = vals.get('first_name', self.first_name)
            if first_name:
                first_name = first_name.title()
                vals['first_name'] = first_name

            name = first_name

            last_name = vals.get('last_name', self.last_name)
            if last_name:
                last_name = last_name.title()
                vals['last_name'] = last_name
                name = name + ' ' + last_name

            vals['name'] = name
        res = super().write(vals)
        if not self.section_id:
            if self.batch_id and len(self.batch_id.section_ids) == 1:
                self.section_id = self.batch_id.section_ids[0].id
        if vals.get('user_id',False) and not auto:
            self.user_id.write({
                'user_type': 'student',
                'student_id': self.id,
                'auto': True,
            })
        return res

    @api.constrains('cnic')
    def _check_cnic(self):
        for rec in self:
            if rec.cnic:
                cnic_com = re.compile('^[0-9+]{5}-[0-9+]{7}-[0-9]{1}$')
                a = cnic_com.search(rec.cnic)
                if a:
                    return True
                else:
                    raise UserError(_("CNIC Format is Incorrect. Format Should like this 00000-0000000-0"))
        return True

    @api.constrains('date_of_birth')
    def _check_birthdate(self):
        for record in self:
            if record.date_of_birth > fields.Date.today():
                raise ValidationError(_("Birth Date can't be greater than Current Date!"))

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Students'),
            'template': '/alifzerocms/static/xls/alifzerocms_student.xlsx'
        }]

    def create_user(self):
        group_portal = self.env.ref('base.group_portal')
        for record in self:
            if not record.user_id:
                data = {
                    'name': record.name + ' ' + (record.last_name or ''),
                    'partner_id': record.partner_id.id,
                    'student_id': record.id,
                    'user_type': 'student',
                    'login': record.id_number or record.entryID or record.email,
                    'password': record.mobile or '123456',
                    'groups_id': group_portal,
                }
                user = self.env['res.users'].create(data)
                record.user_id = user.id

    def compute_previous_year_date(self, strdate):
        tenyears = relativedelta(years=16)
        start_date = fields.Date.from_string(strdate)
        return fields.Date.to_string(start_date - tenyears)

    @api.depends('code')
    def _get_import_identifier(self):
        for rec in self:
            identifier = self.env['ir.model.data'].search(
                [('model', '=', 'alifzerocms.student'), ('res_id', '=', rec.id)])
            if identifier:
                identifier.module = 'ST'
                identifier.name = rec.code or rec.id
            else:
                data = {
                    'name': rec.code or rec.id,
                    'module': 'ST',
                    'model': 'alifzerocms.student',
                    'res_id': rec.id,
                }
                identifier = self.env['ir.model.data'].create(data)

            rec.import_identifier = identifier.id

    def lock(self):
        for rec in self:
            if rec.batch_id:
                rec.state = 'enroll'
                if not rec.term_id:
                    rec.term_id = rec.batch_id.term_id.id
                if not rec.semester_id:
                    rec.semester_id = rec.batch_id.semester_id.id
            else:
                raise UserError('Please Assign Batch to Student.')

    def cron_account(self):
        recs = self.env['res.partner'].search(['|', ('property_account_receivable_id', '=', False), ('property_account_payable_id', '=', False)])
        for rec in recs:
            rec.property_account_receivable_id = 3
            rec.property_account_payable_id = 229

    def cron_pass(self):
        for rec in self:
            if rec.mobile:
                rec.mobile = rec.mobile.replace('-', '')
                if rec.user_id:
                    rec.user_id.password = rec.mobile

    def cron_reg(self):
        for rec in self.env['alifzerocms.assesment.obe.summary'].search([('registration_id','=',False)]):
            reg = self.env['alifzerocms.student.course'].search([('student_id','=',rec.student_id.id),('class_id','=',rec.class_id.id)])
            rec.registration_id = rec.id

    def process_images(self):
        # source = "ftp/files/"
        source = self.env['ir.config_parameter'].sudo().get_param('alifzerocms.ftp_server_source')
        destination = "/tmp/"
        self.downloadFiles(source, destination)
        os.chdir(destination + source)
        image_list = os.listdir()
        students = self.env['alifzerocms.student'].search([])
        for img in image_list:
            for rec in students:
                if rec.id_number and rec.id_number == os.path.splitext(img)[0]:
                    pic = open(destination + source + img, 'rb')
                    pic_binary = pic.read()
                    pic_binary2 = bytearray(pic_binary)
                    if pic_binary:
                        rec.image = codecs.encode(pic_binary, 'base64')
                        # pic_binary2 = base64.b64encode(pic.read())
                        # pic_binary2 = pic_binary.decode('base64')

    # def downloadFiles(self, path, destination):
    #     # server = "127.0.0.1"
    #     # user = "testftp"
    #     # password = "123"
    #
    #     server = self.env['ir.config_parameter'].sudo().get_param('alifzerocms.ftp_server_address')
    #     user = self.env['ir.config_parameter'].sudo().get_param('alifzerocms.ftp_server_user')
    #     password = self.env['ir.config_parameter'].sudo().get_param('alifzerocms.ftp_server_password')
    #
    #     interval = 0.05
    #
    #     ftp = ftplib.FTP(server)
    #     ftp.login(user, password)
    #
    #     try:
    #         ftp.cwd(path)
    #         os.chdir(destination)
    #         self.mkdir_p(destination[0:len(destination)] + path)
    #         print("Created: " + destination[0:len(destination)] + path)
    #     except OSError:
    #         pass
    #     except ftplib.error_perm:
    #         print("Error: could not change to " + path)
    #         sys.exit("Ending Application")
    #
    #     filelist = ftp.nlst()
    #
    #     for file in filelist:
    #         time.sleep(interval)
    #         try:
    #             ftp.cwd(path + file + "/")
    #             self.downloadFiles(path + file + "/", destination[0:len(destination)] + path)
    #         except ftplib.error_perm:
    #             os.chdir(destination[0:len(destination)])
    #
    #             try:
    #                 ftp.retrbinary("RETR " + file, open(os.path.join(destination[0:len(destination)] + path, file), "wb").write)
    #                 print("Downloaded: " + file)
    #             except:
    #                 print("Error: File could not be downloaded " + file)
    #     return
    #
    # def mkdir_p(self, path):
    #     try:
    #         os.makedirs(path)
    #     except OSError as exc:
    #         if os.path.isdir(path):
    #             pass
    #         else:
    #             raise




class alifzerocmsStudentAcademic(models.Model):
    _name = 'alifzerocms.student.academic'
    _description = 'Student Academics'
    
    degree_level = fields.Selection([('matric', 'Matric'),('o-level', 'O-Level'),('dae', 'DAE'), ('inter', 'Intermediate'),('a-level', 'A-Level')], 'Degree Level', required=1)
    degree = fields.Char('Degree', required=1)
    year = fields.Char('Passing Year')
    board = fields.Char('Board Name')
    subjects = fields.Char('Subjects')
    total_marks = fields.Integer('Total Marks', required=1)
    obtained_marks = fields.Integer('Obtained Marks', required=1)
    student_id = fields.Many2one('alifzerocms.student', 'Student')
    
        
class alifzerocmsStChangeStateRule(models.Model):
    _name = 'alifzerocms.student.change.state.rule'
    _description = "Reason for Changing Student State"
    _order = 'sequence'

    name = fields.Text(string='Reason', help='Define the Reason To Change the State of Student')
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer('Color')


class alifzerocmsStudentProfileAttribute(models.Model):
    _name = 'alifzerocms.student.profilechange.attribute'
    _description = "Attributes Allowed for Student Profile Change"

    name = fields.Char('Name')
    # field_name_id = fields.Many2one('ir.model.fields', 'Change Allowed In', required= True)


class alifzerocmsStudentComment(models.Model):
    _name = 'alifzerocms.student.comment'
    _description = 'Student Comment'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'student_id'

    student_id = fields.Many2one('alifzerocms.student', 'Student', required=True)
    name = fields.Char(string = 'Student Name', related = 'student_id.name', readonly=True, store = True)
    message_from = fields.Char(string='Message From', readonly=True)
    # program_id = fields.Many2one('alifzerocms.program', string = 'Program', related = 'student_id.program_id', readonly=True, store = True)
    comment = fields.Html(string="Comment", required=True)

    date = fields.Date('Comment Date', default=date.today(), readonly=1)
    notfication_date = fields.Date('Notification Date', default=date.today())
    message_ref = fields.Char(string="Reference Number", required=True)

    cms_ref = fields.Char(string="CMS Reference Number", required=True)

