from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import pdb


class alifzerocmsApplicationSteps(models.Model):
    _name = 'alifzerocms.application.steps'
    _description = 'Application Steps'
    _order = 'sequence'

    name = fields.Char('Step Name',required=True)
    sequence = fields.Integer('Sequence',required=True)
    template = fields.Many2one('ir.ui.view', 'Template', required=True, domain=[('type','=','qweb')])
    test_field = fields.Many2one('ir.model.fields', 'Completion Test Field', domain=[('model','=','alifzerocms.application')])
    invisible = fields.Char()
    active = fields.Boolean(default=True)


class alifzerocmsAdmissionRegister(models.Model):
    _inherit = "alifzerocms.admission.register"

    def _compute_aggregate(self):
        for rec in self.application_ids.filtered(lambda l: l.state in ('verified', 'confirm')).with_progress(msg="Aggregate Calculation"):
            for academic in rec.academic_ids:
                if academic.degree_level in ('Intermediate', 'DAE'):
                    if academic.physics_total_marks and academic.physics_marks:
                        academic.physics_marks_per = academic.physics_marks / (academic.physics_total_marks or 1) * 100
                    if academic.math_total_marks and academic.math_marks:
                        academic.math_marks_per = academic.math_marks / (academic.math_total_marks or 1) * 100
                    if academic.add_math_total_marks and academic.add_math_marks:
                        academic.add_math_marks_per = academic.add_math_marks / (academic.add_math_total_marks or 1) * 100
                    if academic.chemistry_total_marks and academic.chemistry_marks:
                        academic.chemistry_marks_per = academic.chemistry_marks / (academic.chemistry_total_marks or 1) * 100
                    if academic.computer_total_marks and academic.computer_marks:
                        academic.computer_marks_per = academic.computer_marks / (academic.computer_total_marks or 1) * 100

                if academic.degree_level == 'Matric':  # SARFRAZ
                    academic.percentage = academic.obtained_marks / (academic.total_marks or 1) * 100

                if academic.degree_level == 'O-Level':  # SARFRAZ
                    academic.o_level_percentage = academic.o_level_obtained / (academic.o_level_total or 1) * 100

                if academic.degree_level == 'A-Level':  # SARFRAZ
                    academic.a_level_percentage = academic.a_level_obtained / (academic.a_level_total or 1) * 100

                if academic.degree_level == 'Intermediate':  # SARFRAZ
                    academic.percentage = academic.obtained_marks / (academic.total_marks or 1) * 100

                if academic.degree_level == 'DAE':  # SARFRAZ
                    academic.dae_percentage = academic.dae_obtainedmarks / (academic.dae_totalmarks or 1) * 100

            rec._get_marks()
            rec.compute_aggregate()

    def sort_applications(self):
        i = 1
        application_ids = self.application_ids.filtered(lambda l: l.state in ('verified','confirm'))

        rejected_applications = self.env['alifzerocms.application']
        # for app in application_ids.filtered(lambda l: l.test_percentage < 0.0):
        #     rejected_applications += app
        #     app.reject_reason_des = 'Less than 50% scored in Test.'
        # application_ids = application_ids - rejected_applications

        # rejected_applications = self.env['alifzerocms.application']
        # for app in application_ids.filtered(lambda l: l.ssc_percentage < 60.0):
        #     rejected_applications += app
        #     app.reject_reason_des = 'Less than 60% scored in O-Level/Matric Exam.'
        # application_ids = application_ids - rejected_applications

        for application in application_ids.sorted(key=lambda r: r.total_aggregates, reverse=True):
            # for application in self.application_ids.filtered(lambda l: l.state in ('approve', 'open', 'submit')).sorted(key=lambda r: r.manual_score, reverse=True):

            if not application.preference_ids:
                raise UserError('Program Preference not set for %s - %s not Set.' % (application.application_no, application.name))

            # if self.information_gathering:
            #     application.write({
            #         'program_id': application.preference_ids and application.preference_ids[0].program_id.id,
            #         'locked': True,
            #         'state': 'open',
            #         'preference': 1,
            #     })

            # if application.cnic and len(application.cnic) == 13:
            #     application.cnic = application.cnic[:5] + '-' + application.cnic[5:12] + '-' + application.cnic[12:]

            application.merit_number = i
            i += 1
            application.state = 'verified'

    # def _compute_quota_details(self):
    #     for rec in self.application_ids.with_progress(msg="Getting Quota Details"):
    #         if rec.inter_specialization in ('dae-e', 'dae-m', 'dae-c', 'dae-other'):
    #             quota = self.env['alifzerocms.admission.quota'].search([('name', '=', 'dae')])
    #             if quota:
    #                 rec.dae_quota_id = quota.id
    #             else:
    #                 raise UserError('Please define Quota with name DAE!')
    #         else:
    #             if rec.is_rural_quota and rec.rural_quota:
    #                 quota = self.env['alifzerocms.admission.quota'].search([('name', '=', rec.rural_quota)])
    #                 if quota:
    #                     rec.quota_id = quota.id
    #
    #             if rec.is_forces_quota and rec.forces_quota:
    #                 quota = self.env['alifzerocms.admission.quota'].search([('name', '=', rec.forces_quota)])
    #                 if quota:
    #                     rec.quota_id2 = quota.id

    def _compute_quota_details(self):
        for rec in self.application_ids.with_progress(msg="Getting Quota Details"):
            if rec.inter_specialization in ('dae-e', 'dae-m', 'dae-c', 'dae-other'):
                quota = self.env['alifzerocms.admission.quota'].search([('name', '=', 'dae')])
                if quota:
                    rec.dae_quota_id = quota.id
                else:
                    raise UserError('Please define Quota with name DAE!')

            if rec.is_rural_quota and rec.rural_quota:
                quota = self.env['alifzerocms.admission.quota'].search([('name', '=', rec.rural_quota)])
                if quota:
                    rec.quota_id = quota.id

            if rec.is_forces_quota and rec.forces_quota:
                quota = self.env['alifzerocms.admission.quota'].search([('name', '=', rec.forces_quota)])
                if quota:
                    rec.quota_id2 = quota.id

    def merit_list(self, merit_register):
        allocation_id = self.env['alifzerocms.admission.allocation'].search([('academic_session_id', '=', self.academic_session_id.id), ('career_id', '=', self.career_id.id)])
        application_ids = self.application_ids.filtered(lambda l: l.state in ('verified', 'approve') and l.locked != True)
        for application in application_ids.filtered(lambda l: l.merit_number > 0).sorted(key=lambda r: r.merit_number):
            if application.locked:
                open_merit_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == application.program_id.id and k.category == 'open_merit')
                quota_merit_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == application.program_id.id and k.category == 'quota' and k.quota_id == application.admission_quota_id)

                prg_merit_cnt = self.env['alifzerocms.application.merit.line'].search_count([
                    ('merit_register_id', '=', merit_register.id), ('program_id', '=', application.program_id.id)])
                quota_merit_cnt = len(self.env['alifzerocms.application.merit.line'].search([
                    ('merit_register_id', '=', merit_register.id), ('program_id', '=', application.program_id.id), ('admission_on_quota', '=', True)
                ]).filtered(lambda l: l.quota_id == application.admission_quota_id))

                merit_lines = []
                merit_line = {
                    'program_id': application.program_id.id,
                    'preference': application.preference,
                    'program_merit_number': prg_merit_cnt + 1,
                    'seats': open_merit_line.seats,
                    'selected': True,
                }
                if application.admission_quota_id and quota_merit_line:
                    merit_line['admission_on_quota'] = True
                    if application.admission_quota_id.type == 'rural':
                        merit_line['quota_id'] = application.quota_id.id
                        merit_line['quota_number'] = quota_merit_cnt + 1
                        merit_line['quota_seats'] = quota_merit_line.seats
                    elif application.admission_quota_id.type == 'forces':
                        merit_line['quota_id2'] = application.quota_id.id
                        merit_line['quota_number2'] = quota_merit_cnt+ 1
                        merit_line['quota_seats2'] = quota_merit_line.seats
                    elif application.admission_quota_id.type == 'other':
                        merit_line['dae_quota_id'] = application.dae_quota_id.id
                        merit_line['dae_quota_number'] = quota_merit_cnt + 1
                        merit_line['dae_seats'] = quota_merit_line.seats
                merit_lines.append([0, 0, merit_line])
                merit_ids = application.merit_ids

                data = {
                    'register_id': self.id,
                    'application_id': application.id,
                    'program_id': application.program_id.id,
                    'preference': application.preference,
                    'merit_register_id': merit_register.id,
                    'program_merit_number': prg_merit_cnt + 1,
                    'merit_number': application.merit_number,
                    'quota_number': False,
                    'quota_id': False,
                    'admission_on_quota': False,
                    'date_interview': False,
                    'state': 'done',
                    'locked': True,
                    'line_ids': merit_lines,
                }
                if application.admission_quota_id:
                    data['admission_on_quota'] = True
                    data['quota_id'] = application.admission_quota_id.id
                    data['quota_number'] = quota_merit_cnt + 1

                app_merit = self.env['alifzerocms.application.merit'].create(data)
                if merit_ids:
                    merit_ids[0].next_merit_app_id = app_merit.id
                    app_merit.prev_merit_app_id = merit_ids[0].id

            else:
                merit_lines = []
                for preference in application.preference_ids.filtered(lambda p:p.type == 'Regular').sorted(key=lambda r: r.preference):
                    open_merit_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == preference.program_id.id and k.category == 'open_merit')
                    quota_merit_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == preference.program_id.id and k.category == 'quota' and k.quota_id == application.quota_id)
                    dae_merit_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == preference.program_id.id and k.category == 'quota' and k.quota_id == application.dae_quota_id)

                    if not open_merit_line:
                        raise ValidationError(_("Seats not defined for %s-%s-%s for Open Merit." % (preference.program_id.name, application.name, application.id)))

                    if application.quota_id and not quota_merit_line:
                        raise ValidationError(_("Seats not defined for %s-%s-%s for Rural Quota." % (preference.program_id.name, application.name, application.id)))

                    if application.dae_quota_id and not dae_merit_line and preference.program_id.code != 'BSCS':
                        raise ValidationError(_("Seats not defined for %s-%s-%s for DAE Quota." % (preference.program_id.name, application.name, application.id)))

                    if self.env['alifzerocms.admission.merit.criteria'].get_eligibility(preference.program_id, application):

                        prg_merit_cnt = self.env['alifzerocms.application.merit.line'].search_count([
                            ('merit_register_id', '=', merit_register.id), ('program_id', '=', preference.program_id.id), ('dae_quota_id', '=', False)
                        ])
                        quota_merit_cnt = len(self.env['alifzerocms.application.merit.line'].search([
                            ('merit_register_id', '=', merit_register.id), ('program_id', '=', preference.program_id.id), ('admission_on_quota', '=', True)
                        ]).filtered(lambda l: l.quota_id == application.quota_id))

                        dae_merit_cnt = len(self.env['alifzerocms.application.merit.line'].search([
                            ('merit_register_id', '=', merit_register.id), ('program_id', '=', preference.program_id.id), ('admission_on_quota', '=', True)
                        ]).filtered(lambda l: l.dae_quota_id == application.dae_quota_id))

                        merit_line = {
                            # 'application_merit_id':
                            'program_id': preference.program_id.id,
                            'preference': preference.preference,
                            'program_merit_number': prg_merit_cnt + 1,
                            'seats': open_merit_line.seats,
                            'admission_on_quota': False,
                        }
                        if application.dae_quota_id and application.inter_specialization in ('dae-e', 'dae-m', 'dae-c', 'dae-other') and preference.program_id.code != 'BSCS':
                            merit_line['dae_quota_id'] = application.dae_quota_id.id
                            merit_line['dae_quota_number'] = dae_merit_cnt + 1
                            merit_line['dae_seats'] = dae_merit_line.seats
                            merit_line['admission_on_quota'] = dae_merit_cnt < dae_merit_line.seats
                            merit_line['selected'] = (dae_merit_cnt < dae_merit_line.seats)
                        else:
                            merit_line['selected'] = (prg_merit_cnt < open_merit_line.seats)
                            if application.quota_id and not merit_line['selected']:
                                merit_line['quota_id'] = application.quota_id.id
                                merit_line['quota_number'] = quota_merit_cnt + 1
                                merit_line['quota_seats'] = quota_merit_line.seats
                                merit_line['admission_on_quota'] = (prg_merit_cnt >= open_merit_line.seats) and (quota_merit_cnt < quota_merit_line.seats)
                                if not merit_line['selected']:
                                    merit_line['selected'] = quota_merit_cnt < quota_merit_line.seats

                        merit_lines.append([0, 0, merit_line])
                        if application.inter_specialization not in ('dae-e', 'dae-m', 'dae-c', 'dae-other') or preference.program_id.code == 'BSCS':
                            if prg_merit_cnt < open_merit_line.seats:
                                merit_ids = application.merit_ids
                                data = {
                                    'register_id': self.id,
                                    'application_id': application.id,
                                    'program_id': preference.program_id.id,
                                    'preference': preference.preference,
                                    'merit_register_id': merit_register.id,
                                    'merit_number': application.merit_number,
                                    'program_merit_number': prg_merit_cnt + 1,
                                    'line_ids': merit_lines,
                                }
                                if open_merit_line.merit_closed_one > application.total_aggregates or open_merit_line.merit_closed_one == 0:
                                    open_merit_line.merit_closed_one = application.total_aggregates
                                app_merit = self.env['alifzerocms.application.merit'].create(data)
                                if merit_ids:
                                    merit_ids[0].next_merit_app_id = app_merit.id
                                    app_merit.prev_merit_app_id = merit_ids[0].id

                                application.program_id = preference.program_id.id
                                application.preference = preference.preference
                                application.admission_quota_id = False

                                

                                # app_merit.amount = application._get_fee_amount()
                                # app_merit.amount = 0
                                break
                            elif application.quota_id and quota_merit_cnt < quota_merit_line.seats:
                                merit_ids = application.merit_ids
                                data = {
                                    'register_id': self.id,
                                    'application_id': application.id,
                                    'program_id': preference.program_id.id,
                                    'preference': preference.preference,
                                    'merit_register_id': merit_register.id,
                                    'merit_number': application.merit_number,
                                    'quota_number': quota_merit_cnt + 1,
                                    'quota_id': application.quota_id.id,
                                    'admission_on_quota': True,
                                    'line_ids': merit_lines,
                                }
                                if quota_merit_line.merit_closed_one > application.total_aggregates or quota_merit_line.merit_closed_one == 0:
                                    quota_merit_line.merit_closed_one = application.total_aggregates
                                app_merit = self.env['alifzerocms.application.merit'].create(data)
                                if merit_ids:
                                    merit_ids[0].next_merit_app_id = app_merit.id
                                    app_merit.prev_merit_app_id = merit_ids[0].id

                                application.program_id = preference.program_id.id
                                application.preference = preference.preference
                                application.admission_quota_id = application.quota_id.id or False

                                
                                # app_merit.amount = application._get_fee_amount()
                                # app_merit.amount = 0
                                break

                        elif dae_merit_cnt < dae_merit_line.seats:
                            merit_ids = application.merit_ids
                            data = {
                                'register_id': self.id,
                                'application_id': application.id,
                                'program_id': preference.program_id.id,
                                'preference': preference.preference,
                                'merit_register_id': merit_register.id,
                                'merit_number': application.merit_number,
                                'quota_number': dae_merit_cnt + 1,
                                'quota_id': application.dae_quota_id.id,
                                'admission_on_quota': True,
                                'line_ids': merit_lines,
                            }
                            if dae_merit_line.merit_closed_one > application.total_aggregates or dae_merit_line.merit_closed_one == 0:
                                dae_merit_line.merit_closed_one = application.total_aggregates
                            app_merit = self.env['alifzerocms.application.merit'].create(data)
                            if merit_ids:
                                merit_ids[0].next_merit_app_id = app_merit.id
                                app_merit.prev_merit_app_id = merit_ids[0].id

                            application.program_id = preference.program_id.id
                            application.preference = preference.preference
                            application.admission_quota_id = application.dae_quota_id.id or False

                            
                            # app_merit.amount = application._get_fee_amount()
                            # app_merit.amount = 0
                            break

                merit_app = self.env['alifzerocms.application.merit'].search([('application_id','=',application.id),('merit_register_id','=',merit_register.id)])
                if not merit_app and application.quota_id2:
                    for preference in application.preference_ids.filtered(lambda p: p.type == 'Armed Forces').sorted(key=lambda r: r.preference):
                        quota_merit_line2 = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == preference.program_id.id and k.category == 'quota' and k.quota_id == application.quota_id2)

                        if application.quota_id2 and not quota_merit_line2:
                            raise ValidationError(_("Seats not defined for %s-%s-%s for Forces Quota." % (preference.program_id.name, application.name, application.id)))

                        if self.env['alifzerocms.admission.merit.criteria'].get_eligibility(preference.program_id, application):

                            quota_merit_cnt2 = len(self.env['alifzerocms.application.merit.line'].search([
                                ('merit_register_id', '=', merit_register.id), ('program_id', '=', preference.program_id.id), ('admission_on_quota', '=', True)
                            ]).filtered(lambda l: l.quota_id2 == application.quota_id2))

                            merit_line = {
                                # 'application_merit_id':
                                'program_id': preference.program_id.id,
                                'preference': preference.preference,
                                'admission_on_quota': False,
                            }
                            if application.inter_specialization not in ('dae-e', 'dae-m', 'dae-c', 'dae-other') or preference.program_id.code == 'BSCS':
                                merit_line['selected'] = (quota_merit_cnt2 < quota_merit_line2.seats)
                                if application.quota_id2:
                                    merit_line['quota_id2'] = application.quota_id2.id
                                    merit_line['quota_number2'] = quota_merit_cnt2 + 1
                                    merit_line['quota_seats2'] = quota_merit_line2.seats
                                    merit_line['admission_on_quota'] = (quota_merit_cnt2 < quota_merit_line2.seats)
                                    merit_line['selected'] = (quota_merit_cnt2 < quota_merit_line2.seats)

                            merit_lines.append([0, 0, merit_line])
                            if application.inter_specialization not in ('dae-e', 'dae-m', 'dae-c', 'dae-other') or preference.program_id.code == 'BSCS':
                                if quota_merit_cnt2 < quota_merit_line2.seats:
                                    merit_ids = application.merit_ids
                                    data = {
                                        'register_id': self.id,
                                        'application_id': application.id,
                                        'program_id': preference.program_id.id,
                                        'preference': preference.preference,
                                        'merit_register_id': merit_register.id,
                                        'merit_number': application.merit_number,
                                        'quota_number': quota_merit_cnt2 + 1,
                                        'quota_id': application.quota_id2.id,
                                        'admission_on_quota': True,
                                        'line_ids': merit_lines,
                                    }
                                    if quota_merit_line2.merit_closed_one > application.total_aggregates or quota_merit_line2.merit_closed_one == 0:
                                        quota_merit_line2.merit_closed_one = application.total_aggregates
                                    app_merit = self.env['alifzerocms.application.merit'].create(data)
                                    if merit_ids:
                                        merit_ids[0].next_merit_app_id = app_merit.id
                                        app_merit.prev_merit_app_id = merit_ids[0].id

                                    application.program_id = preference.program_id.id
                                    application.preference = preference.preference

                                    if not preference.program_id.code == 'BSCS':
                                        application.admission_quota_id = application.quota_id2.id or False


                                    # app_merit.amount = application._get_fee_amount()
                                    # app_merit.amount = 0
                                    break

        self.state = 'merit'


    def start_admission(self):
        self._compute_aggregate()
        self.sort_applications()
        self._compute_quota_details()
        self.state = 'admission'
