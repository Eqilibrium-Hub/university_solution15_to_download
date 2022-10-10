import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class alifzerocmsBuilding(models.Model):
    _name = 'alifzerocms.building'
    _description = "Building"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence desc'

    name = fields.Char('Name')
    code = fields.Char('Code')  # abbreviation
    sequence = fields.Integer('Sequence')
    externalId = fields.Char('Ecternal ID')
    locationX = fields.Float('Location X')
    locationY = fields.Float('Location Y')
    institute_id = fields.Many2one('alifzerocms.institute', string='Institute',required=True)
    unitime_id = fields.Integer()


class alifzerocmsRoomType(models.Model):
    _name = 'alifzerocms.room.type'
    _description = "Room Type"

    name = fields.Char('Name')
    code = fields.Char('Code')
    type = fields.Selection([('Room', 'Room'), ('Other', 'Other')], 'Room Type', default='Room')
    unitime_id = fields.Integer()


class alifzerocmsRoom(models.Model):
    _name = 'alifzerocms.room'
    _description = "Class Room"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence desc'

    name = fields.Char('Room Name')
    code = fields.Char('Room Number')  # roomNumber
    building_id = fields.Many2one('alifzerocms.building', 'Building',required=True)
    room_type = fields.Many2one('alifzerocms.room.type', 'Room Type')  # domain Room
    sequence = fields.Integer('Sequence')
    capacity = fields.Integer('Capacity')
    examCapacity = fields.Integer('Exam Capacity')
    externalId = fields.Char('External ID')
    locationX = fields.Float('Location X', help='X Coordinates')
    locationY = fields.Float('Location Y', help='Y Coordinates')
    area = fields.Float('Area', help='Square Feet')
    controlDepartment = fields.Many2one('alifzerocms.department', 'Control Department')
    eventDepartment = fields.Many2one('alifzerocms.department', 'Event Department')
    instructional = fields.Boolean('Instructional')
    roomClassification = fields.Char('Classification')
    scheduledRoomType = fields.Selection(
        [('computingLab', 'computingLab'), ('departmental', 'departmental'), ('genClassroom', 'genClassroom')],
        'Scheduled Room Type')
    eventNote = fields.Text('Event Note')
    roomSharingNote = fields.Text('Room Sharing Note')

    feature_ids = fields.One2many('alifzerocms.room.feature', 'class_room_id', string='Class Amenities')

    def sync_unitime_odoo(self, rooms):
        for room in rooms:
            extra = room['extra']
            del room['extra']

            if extra.get('building', False):
                building = extra.get('building', False)
                building_data = {
                    'unitime_id': building.get('id', False),
                    'code': building.get('abbreviation', False),
                    'name': building.get('Purdue Village Apts #113'),
                    'locationX': building.get('x', False),
                    'locationY': building.get('y', False),
                    'externalId': building.get('externalId', False),
                }
                building = self.env['alifzerocms.building'].search([('code', '=', building_data['code'])])
                if not building:
                    building = self.env['alifzerocms.building'].create(building_data)
                else:
                    building.write(building_data)
                room['building_id'] = building.id

            if extra.get('roomType', False):
                roomType = extra.get('roomType', False)
                roomType_data = {
                    'unitime_id': roomType.get('id', False),
                    'code': roomType.get('reference', False),
                    'name': roomType.get('label', False),
                }
                rtype = self.env['alifzerocms.room.type'].search([('unitime_id', '=', roomType_data['unitime_id'])])
                if not rtype:
                    rtype = self.env['alifzerocms.room.type'].create(roomType_data)
                else:
                    rtype.write(roomType_data)
                room['room_type'] = rtype.id

            if room.get('eventDepartment', False):
                room['eventDepartment'] = self.env['alifzerocms.department'].search(
                    [('code', '=', room['eventDepartment']['code'])])
            pattern = self.env['alifzerocms.room'].search([('code', '=', room['code'])])
            if not pattern:
                pattern = self.env['alifzerocms.room'].search([('name', '=', room['name'])])
            if not pattern:
                pattern = self.env['alifzerocms.room'].create(room)
            else:
                pattern.write(room)

            if extra.get('features', False):
                features = extra.get('features', False)
                for feature in features:
                    feature_data = {
                        'unitime_id': feature.get('id', False),
                        'code': feature.get('abbv', False),
                        'name': feature.get('label', False),
                    }
                amenities = self.env['alifzerocms.amenities'].search([('unitime_id', '=', feature_data['unitime_id'])])
                if not amenities:
                    amenities = self.env['alifzerocms.amenities'].create(feature_data)
                else:
                    amenities.write(feature_data)

                feature_id = self.env['alifzerocms.room.feature'].search(
                    [('name', '=', amenities.id), ('class_room_id', '=', pattern.id)])
                if not feature_id:
                    self.env['alifzerocms.room.feature'].create({
                        'name': amenities.id,
                        'class_romm_id': pattern.id
                    })


class alifzerocmsRoomFeature(models.Model):
    _name = 'alifzerocms.room.feature'
    _description = "Amenities in Class"

    name = fields.Many2one('alifzerocms.amenities', string="Amenities", help="Select the amenities in Class Room")
    qty = fields.Float(string='Quantity', help="The quantity of the amenities", default=1.0)
    class_room_id = fields.Many2one('alifzerocms.room', string="Class Room")

    @api.constrains('qty')
    def check_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Quantity must be Positive'))


class alifzerocmsAmenities(models.Model):
    _name = 'alifzerocms.amenities'
    _description = 'Amenities in Institution'
    _order = 'name asc'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, help='Name of Amenity')
    code = fields.Char(string='Code', help='Code of Amenity')
    unitime_id = fields.Integer()

    _sql_constraints = [
        ('code', 'unique(code)', "Another Amenity already exists with this code!"),
    ]


# class ResCompany(models.Model):
#     _inherit = 'res.company'
#
#     affiliation = fields.Char(string='Affiliation')
#     register_num = fields.Char(string='Register')
#     signature = fields.Binary('Signature')
#     accreditation = fields.Text('Accreditation')
#     approval_authority = fields.Text('Approval Authority')


class alifzerocmsReligion(models.Model):
    _name = 'alifzerocms.religion'
    _description = 'Religion'
    _order = 'sequence'

    name = fields.Char(string="Religion", required=True)
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer('Color')
    

class alifzerocmsCity(models.Model):
    _name = 'alifzerocms.city'
    _description = 'City'
    _order = 'sequence'

    name = fields.Char(string="City", required=True)
    code = fields.Char(string="City Code", required=True)
    sequence = fields.Integer(string='Sequence')


class alifzerocmsProvince(models.Model):
    _name = 'alifzerocms.province'
    _description = 'Province'
    _order = 'sequence'

    country_id = fields.Many2one('res.country', string="Country")
    name = fields.Char(string="Province", required=True)
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string='Sequence')
    domicile_ids = fields.One2many('alifzerocms.domicile', 'province_id', string='Domiciles')
    district_ids = fields.One2many('alifzerocms.district', 'province_id', string="Districts")


class alifzerocmsDistrict(models.Model):
    _name = 'alifzerocms.district'
    _description = 'District'
    _order = 'sequence'

    province_id = fields.Many2one('alifzerocms.province', string="Province")
    name = fields.Char('District Name',size=32, required=True)
    code = fields.Char('Code', size=8, required=True)
    sequence = fields.Integer(string='Sequence')


class alifzerocmsDomicile(models.Model):
    _name = 'alifzerocms.domicile'
    _description = 'Domicile'
    _order = 'sequence'

    name = fields.Char(string="Domicile Region", required=True)
    code = fields.Char(string="Code", required=True)
    province_id = fields.Many2one('alifzerocms.province', string='Province')
    sequence = fields.Integer(string='Sequence')


class alifzerocmsMartialStatus(models.Model):
    _name = 'alifzerocms.marital.status'
    _description = 'Marital Status'
    _order = 'sequence'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer('Color')
    

class alifzerocmsProfesions(models.Model):
    _name = 'alifzerocms.profs'
    _description = 'Professions'
    _order = 'sequence'

    code = fields.Char(string="Code", help="Code")
    name = fields.Text(string="Description", required=False, )
    sequence = fields.Integer(string='Sequence')
    
    
class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    def name_get(self):
        # model_id_name = defaultdict(dict)  # {res_model: {res_id: name}}
        # for xid in self:
        #    model_id_name[xid.model][xid.res_id] = None
        #
        # fill in model_id_name with name_get() of corresponding records
        # for model, id_name in model_id_name.items():
        #    try:
        #        ng = self.env[model].browse(id_name).name_get()
        #        id_name.update(ng)
        #    except Exception:
        #        pass

        # return results, falling back on complete_name
        # return [(xid.id, model_id_name[xid.model][xid.res_id] or xid.complete_name)
        #        for xid in self]

        return [(xid.id, xid.complete_name) for xid in self]


class alifzerocmsTranscript(models.Model):
    _name = 'alifzerocms.transcript.history'
    _description = "Transcript History"

    date = fields.Date('Date', readonly=True)
    student_id = fields.Many2one('alifzerocms.student', string='Student')
    term_id = fields.Many2one('alifzerocms.academic.term', 'Term', readonly=True)
    transcript = fields.Binary('Transcript', readonly=True)


class alifzerocmsPublications(models.Model):
    _name = 'alifzerocms.publication'
    _description = "alifzerocms Publications"

    date = fields.Date('Publication Date')
    name = fields.Char('Name')
    topic = fields.Char('Topic')
    paper_attachment = fields.Binary('Attachment', attachment=True)
    student_id = fields.Many2one('alifzerocms.student', string='Student')
    faculty_staff_id = fields.Many2one('alifzerocms.faculty.staff', string='Faculty')


class alifzerocmsLanguage(models.Model):
    _name = 'alifzerocms.language'
    _description = "alifzerocms Languages"

    name = fields.Char('Name')
    code = fields.Char('Code')
    sequence = fields.Integer(string='Sequence')


class alifzerocmsExtraActivities(models.Model):
    _name = 'alifzerocms.extra.activity'
    _description = "alifzerocms Extra Curricular Activities"

    name = fields.Char('Name')
    remarks = fields.Html('Remarks')
    date = fields.Date('Date')
    student_id = fields.Many2one('alifzerocms.student', string='Student')
    faculty_staff_id = fields.Many2one('alifzerocms.faculty.staff', string='Faculty')


class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'
    
    role_domain = fields.Char('Role Domain')
    
    def _get_role_users(self,program):
        role_domain = eval(self.role_domain)[0]
        check_part = role_domain[0][-21:]   # '.employee_tag_id.name'
        domain_part = role_domain[0][:-21]  # 'institute_id.faculty_ids'
        domain = 'program.' + domain_part   # 'self.program_id.institute_id.faculty_ids'
        
        operator = role_domain[1]   # =, in
        tags = role_domain[2]  # HOD
        faculties = eval(domain)   # alifzerocms.department.line(1, 2, 3)
        if operator == '=':
            faculties = faculties.filtered(lambda l: l.employee_tag_id.name == tags)  # alifzerocms.department.line(1, )
        elif operator == 'in':
            faculties = faculties.filtered(lambda l: l.employee_tag_id.name in [tags])  # alifzerocms.department.line(1, )
        
        if faculties:
            employee = faculties[0].employee_id
            if employee.user_id:
                return employee.user_id.id
            else:
                raise ValidationError('User Account not created for employee: %s' % (employee.name,))
        else:
            raise ValidationError('No User Found for Approval Role: %s' % (tags,))
        
    
class alifzerocmsWeekDays(models.Model):
    _name = 'alifzerocms.week.day'
    _description = 'Week Day'
    _order = 'sequence'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    sequence = fields.Integer('Sequence')
    number = fields.Integer('Number')
    color = fields.Integer('Day Color')


class alifzerocmsErrorReporting(models.Model):
    _name = 'alifzerocms.error.reporting'
    _description = 'Errors Reporting'


    def get_default_user(self):
        return self.env.user.id

    name = fields.Char('Title')
    description = fields.Text('Description')
    reported_on = fields.Datetime('Date', default=datetime.now())
    reported_by_id = fields.Many2one('res.users', 'Reported By', default= get_default_user)
    state = fields.Selection([('draft','Draft'),('submit','Submit'),('done','Done'),('cancel','Cancel')],'Status',default='draft')
    allow_preview = fields.Boolean('Allow Preview', default=True)