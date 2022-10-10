from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import pdb


class alifzerocmsAdmissionRegister(models.Model):
    _name = "alifzerocms.admission.register"
    _description = "Admission Register"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, readonly=True, states={'draft': [('readonly', False)]})
    academic_session_id = fields.Many2one('alifzerocms.academic.session', 'Academic Session', required=True)
    term_id = fields.Many2one('alifzerocms.academic.term', 'Academic Term', required=True)
    career_id = fields.Many2one('alifzerocms.career', 'Career', required=True)
    date_start = fields.Date('Start Date', readonly=True, default=fields.Date.today(),
                             states={'draft': [('readonly', False)]})
    date_end = fields.Date('End Date', readonly=True, default=(fields.Date.today() + relativedelta(days=30)),
                           states={'draft': [('readonly', False)]})

    eligibility_criteria_image = fields.Binary('Eligibility criteria Image', states={'draft': [('readonly', False)]})
    application_ids = fields.One2many('alifzerocms.application', 'register_id', 'Admissions')
    merit_criteria_ids = fields.One2many('alifzerocms.admission.merit.criteria', 'register_id', 'Merit Criteria')
    program_ids = fields.Many2many('alifzerocms.program', 'register_program_rel', 'register_id', 'program_id',
                                   'Offered Programs')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'),
         ('cancel', 'Cancelled'), ('application', 'Application Gathering'), ('sort', 'Application Stoped'),
         ('admission', 'Merit Process'), ('merit', 'Merit'), ('done', 'Done')],
        'Status', default='draft', tracking=True)

    quota_enabled = fields.Boolean('Enable Quota',default=False)
    allocation_id = fields.Many2one('alifzerocms.admission.allocation', 'Quota Allocation')
    merit_register_id = fields.Many2one('alifzerocms.merit.register', 'Merit Register')
    first_merit_register_id = fields.Many2one('alifzerocms.merit.register', 'First Merit Register')
    merit_register_ids = fields.One2many('alifzerocms.merit.register', 'register_id', 'Merit Registers')
    information_gathering = fields.Boolean('For Information Gathering Only', default=False)


    # For aggregate Calulation
    matric_o_level_score = fields.Float('Matric / O-Level', default=10.0, tracking=True, required=True)
    intermediate = fields.Float('Intermediate', default=25.0, tracking=True, required=True)
    entry_test = fields.Float('Entry Test', default=50.0, tracking=True, required=True)
    physics_marks = fields.Float('Physics Marks', default=5.0, tracking=True, required=True)
    math_marks = fields.Float('Maths/Add Maths Marks', default=5.0, tracking=True, required=True)
    chemistry_marks = fields.Float('Computer/Chemistry Marks', default=5.0, tracking=True, required=True)

    matric_min = fields.Float('Matric Minimum', default=60.0, tracking=True, required=True)
    inter_min = fields.Float('Intermediate Minimum', default=60.0, tracking=True, required=True)
    a_level_min = fields.Float('A Level Minimum', default=60.0, tracking=True, required=True)
    physics_per_min = fields.Float('Physics Minimum', default=60.0, tracking=True, required=True)
    math_per_min = fields.Float('Mathematics Minimum', default=60.0, tracking=True, required=True)
    computer_per_min = fields.Float('Computer Minimum', default=60.0, tracking=True, required=True)
    chemistry_per_min = fields.Float('Chemistry Minimum', default=60.0, tracking=True, required=True)


    def sort_applications(self):
        i = 1
        for application in self.application_ids.filtered(lambda l: l.state in ('approve', 'open', 'submit')).sorted(
                key=lambda r: r.merit_score, reverse=True):
            # for application in self.application_ids.filtered(lambda l: l.state in ('approve', 'open', 'submit')).sorted(key=lambda r: r.manual_score, reverse=True):

            if not application.preference_ids:
                raise UserError(
                    'Program Preference not set for %s - %s not Set.' % (application.entryID, application.name))

            # if self.information_gathering:
            #     application.write({
            #         'program_id': application.preference_ids and application.preference_ids[0].program_id.id,
            #         'locked': True,
            #         'state': 'open',
            #         'preference': 1,
            #     })

            if application.cnic and len(application.cnic) == 13:
                application.cnic = application.cnic[:5] + '-' + application.cnic[5:12] + '-' + application.cnic[12:]

            application.merit_number = i
            i += 1

    def merit_list(self, merit_register, schedule_lines):
        allocation_id = self.env['alifzerocms.admission.allocation'].search(
            [('academic_session_id', '=', self.academic_session_id.id), ('career_id', '=', self.career_id.id)])
        cnt = 1
        for application in self.application_ids.filtered(lambda l: l.state in ('approve', 'open', 'submit')).sorted(
                key=lambda r: r.merit_number):
            if application.locked:
                quota_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == application.program_id.id)
                prg_merit_cnt = self.env['alifzerocms.application.merit.line'].search_count([
                    ('merit_register_id', '=', merit_register.id), ('program_id', '=', application.program_id.id)
                ])
                merit_lines = []
                merit_line = {
                    'program_id': application.program_id.id,
                    'preference': application.preference,
                    'program_merit_number': prg_merit_cnt + 1,
                    'seats': quota_line.seats,
                    'selected': True,
                }
                merit_lines.append([0, 0, merit_line])
                merit_ids = application.merit_ids
                data = {
                    'register_id': self.id,
                    'application_id': application.id,
                    'program_id': application.program_id.id,
                    'preference': application.preference,
                    'merit_register_id': merit_register.id,
                    'merit_number': application.merit_number,
                    'program_merit_number': prg_merit_cnt + 1,
                    'date_interview': False,
                    'state': 'done',
                    'locked': True,
                    'line_ids': merit_lines,
                }
                app_merit = self.env['alifzerocms.application.merit'].create(data)
                if merit_ids:
                    merit_ids[0].next_merit_app_id = app_merit.id
                    app_merit.prev_merit_app_id = merit_ids[0].id

            else:
                schedule = schedule_lines.filtered(lambda l: l.serial_start <= cnt and l.serial_end >= cnt)

                merit_lines = []
                for preference in application.preference_ids.sorted(key=lambda r: r.preference):
                    quota_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == preference.program_id.id)
                    if not quota_line:
                        raise ValidationError(_("Seats not defined for %s-%s-%s" % (
                        preference.program_id.name, application.name, application.id)))

                    prg_merit_cnt = self.env['alifzerocms.application.merit.line'].search_count([
                        ('merit_register_id', '=', merit_register.id), ('program_id', '=', preference.program_id.id)
                    ])
                    merit_line = {
                        # 'application_merit_id':
                        'program_id': preference.program_id.id,
                        'preference': preference.preference,
                        'program_merit_number': prg_merit_cnt + 1,
                        'seats': quota_line.seats,
                        'selected': prg_merit_cnt < quota_line.seats,
                    }
                    merit_lines.append([0, 0, merit_line])
                    if prg_merit_cnt < quota_line.seats:
                        merit_ids = application.merit_ids
                        data = {
                            'register_id': self.id,
                            'application_id': application.id,
                            'program_id': preference.program_id.id,
                            'preference': preference.preference,
                            'merit_register_id': merit_register.id,
                            'merit_number': application.merit_number,
                            'program_merit_number': prg_merit_cnt + 1,
                            'date_interview': schedule and schedule.date_interview or False,
                            'line_ids': merit_lines,
                        }
                        app_merit = self.env['alifzerocms.application.merit'].create(data)
                        if merit_ids:
                            merit_ids[0].next_merit_app_id = app_merit.id
                            app_merit.prev_merit_app_id = merit_ids[0].id

                        application.program_id = preference.program_id.id
                        application.preference = preference.preference
                        app_merit.amount = application._get_fee_amount()
                        # app_merit.amount = 0
                        cnt += 1
                        break

        self.state = 'merit'

    @api.constrains('date_start', 'date_end')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.date_start)
            end_date = fields.Date.from_string(record.date_end)
            if start_date > end_date:
                raise ValidationError(
                    _("End Date cannot be set before Start Date."))

    def confirm_register(self):
        self.state = 'confirm'

    def set_to_draft(self):
        self.state = 'draft'

    def cancel_register(self):
        self.state = 'cancel'

    def start_application(self):
        self.state = 'application'

    def stop_application(self):
        self.state = 'sort'

    def start_admission(self):
        self.sort_applications()
        self.state = 'admission'


class alifzerocmsAdmissionMerit(models.Model):
    _name = "alifzerocms.admission.merit.criteria"
    _description = "Admission Merit Criteria"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    register_id = fields.Many2one('alifzerocms.admission.register', 'Admission Register', required=True)
    program_ids = fields.Many2many('alifzerocms.program', string='Program', required=True)
    matric_percentage = fields.Float('Matric Percentage', default=60,
                                     help='If this is not eligible for any program, Add percentage > 100')
    ol_percentage = fields.Float('O-Levels Percentage', default=60,
                                 help='If this is not eligible for any program, Add percentage > 100')
    pre_en_percentage = fields.Float('Pre-Eng Percentage', default=50,
                                     help='If this is not eligible for any program, Add percentage > 100')
    pre_me_percentage = fields.Float('Pre-Med Percentage', default=50,
                                     help='If this is not eligible for any program, Add percentage > 100')
    pre_me_ad_percentage = fields.Float('Pre-Me with Add Percentage', default=50,
                                        help='If this is not eligible for any program, Add percentage > 100')
    ics_percentage = fields.Float('ICS Percentage', default=50,
                                  help='If this is not eligible for any program, Add percentage > 100')
    a_level_percentage = fields.Float('A-Levels Percentage', default=60,
                                      help='If this is not eligible for any program, Add percentage > 100')
    a_level_com_percentage = fields.Float('A-Levels-Com Percentage', default=50,
                                          help='If this is not eligible for any program, Add percentage > 100')
    dae_percentage = fields.Float('DAE Percentage', default=50,
                                  help='If this is not eligible for any program, Add percentage > 100')
    dae_speciality = fields.Selection([('dae-m', 'Mechanical'), ('dae-e', 'Electrical'), ('dae-c', 'Civil')],
                                      string='DAE Speciality')
    test_percentage = fields.Float('Test Percentage', default=50,
                                   help='If this is not eligible for any program, Add percentage > 100')
    sequence = fields.Integer('Sequence')
    inter_result_status = fields.Selection([('Complete', 'Complete'), ('Result Waited', 'Result Awaiting')],
                                           string='Inter Result Status', default="Complete")

    def get_eligibility(self, program_id, application_id):
        is_eligible = False
        merit_criteria = self.search([('register_id', '=', application_id.register_id.id)]).filtered(
            lambda p: program_id in p.program_ids and p.inter_result_status == application_id.inter_result_status)
        if not merit_criteria:
            raise ValidationError(
                _("Eligibility Criteria is not set for program %s with Exam Result Status %s") % (
                program_id.name, application_id.inter_result_status))

        if application_id.ssc_percentage >= merit_criteria.matric_percentage and application_id.test_percentage >= merit_criteria.test_percentage:
            if application_id.inter_specialization == 'p-che-m' and application_id.nutech_inter_percentage >= merit_criteria.pre_en_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'p-com-m' and application_id.nutech_inter_percentage >= merit_criteria.ics_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'a-p-che-m' and application_id.nutech_inter_percentage >= merit_criteria.a_level_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'a-p-com-m' and application_id.nutech_inter_percentage >= merit_criteria.a_level_com_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'p-che-adm' and application_id.nutech_inter_percentage >= merit_criteria.pre_me_ad_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'p-che-b' and application_id.nutech_inter_percentage >= merit_criteria.pre_me_percentage:
                is_eligible = True
            elif application_id.inter_specialization in (
            'dae-e', 'dae-m', 'dae-c') and application_id.nutech_inter_percentage >= merit_criteria.dae_percentage:
                if (application_id.inter_specialization == merit_criteria.dae_speciality) or (
                not merit_criteria.dae_speciality):
                    is_eligible = True

        return is_eligible

    def cron_get_eligibility(self, program_id, application_id):
        is_eligible = False
        program_id = self.env['alifzerocms.program'].search([('id', '=', program_id)])
        application_id = self.env['alifzerocms.application'].search([('id', '=', application_id)])

        merit_criteria = self.search([('register_id', '=', application_id.register_id.id)]).filtered(
            lambda p: program_id in p.program_ids and p.inter_result_status == application_id.inter_result_status)
        if not merit_criteria:
            raise ValidationError(
                _("Eligibility Criteria is not set for program %s with Exam Result Status %s") % (
                program_id.name, application_id.inter_result_status))

        if application_id.ssc_percentage >= merit_criteria.matric_percentage and application_id.test_percentage >= merit_criteria.test_percentage:
            if application_id.inter_specialization == 'p-che-m' and application_id.nutech_inter_percentage >= merit_criteria.pre_en_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'p-com-m' and application_id.nutech_inter_percentage >= merit_criteria.ics_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'a-p-che-m' and application_id.nutech_inter_percentage >= merit_criteria.a_level_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'a-p-com-m' and application_id.nutech_inter_percentage >= merit_criteria.a_level_com_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'p-che-adm' and application_id.nutech_inter_percentage >= merit_criteria.pre_me_ad_percentage:
                is_eligible = True
            elif application_id.inter_specialization == 'p-che-b' and application_id.nutech_inter_percentage >= merit_criteria.pre_me_percentage:
                is_eligible = True
            elif application_id.inter_specialization in (
            'dae-e', 'dae-m', 'dae-c') and application_id.nutech_inter_percentage >= merit_criteria.dae_percentage:
                if (application_id.inter_specialization == merit_criteria.dae_speciality) or (
                not merit_criteria.dae_speciality):
                    is_eligible = True

        return is_eligible
