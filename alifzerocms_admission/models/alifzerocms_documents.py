
import datetime
from odoo import fields, models, api, _
from datetime import date


class alifzerocmsDocuments(models.Model):
    _name = 'alifzerocms.documents'
    _description = "Student Documents"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('alifzerocms.documents') or _('New')
        res = super(alifzerocmsDocuments, self).create(vals)
        return res


    def verify_document(self):
        for rec in self:
            rec.write({
                'verified_by': self.env.uid,
                'verified_date': datetime.datetime.now().strftime("%Y-%m-%d"),
                'state': 'done'
            })


    def need_correction(self):
        for rec in self:
            rec.write({
                'state': 'correction'
            })


    def hard_copy_returned(self):
        for rec in self:
            if rec.state == 'done':
                rec.write({
                    'state': 'returned',
                    'returned_by': self.env.uid,
                    'returned_date': datetime.datetime.now().strftime("%Y-%m-%d")
                })

    name = fields.Char(string='Serial Number', copy=False, default=lambda self: _('New'))
    document_name = fields.Many2one('document.document', string='Document Type', required=True, help="Choose the Type of the Document")
    description = fields.Text(string='Description', copy=False, help="Enter a Description about the Document")
    has_hard_copy = fields.Boolean(string="Hard Copy Received", help="Tick the field if the hard copy is provided")
    # location_id = fields.Many2one('stock.location', 'Location', domain="[('usage', '=', 'internal')]",
    #     help="Location where which the hard copy is stored")
    location_note = fields.Char(string="Location Note", help="Enter some notes about the location")
    submit_date = fields.Date(string="Submitted Date", default=date.today(),
        help="Documents are submitted on")
    received_by = fields.Many2one('hr.employee', string="Received By", help="The Documents are received by")
    returned_by = fields.Many2one('hr.employee', string="Returned By", help="The Documents are returned by")
    verified_date = fields.Date(string="Verified Date", help="Date at the verification is done")
    returned_date = fields.Date(string="Returned Date", help="Returning date")
    reference = fields.Char(string='Document Number', required=True, copy=False)
    responsible_verified = fields.Many2one('hr.employee', string="V. Responsible")
    responsible_returned = fields.Many2one('hr.employee', string="Ret. Responsible")

    verified_by = fields.Many2one('res.users', string='Verified by')
    application_ref = fields.Many2one('alifzerocms.application', invisible=1, copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id', string="Attachment",
        help='You can attach the copy of your document', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'), ('correction', 'Correction'), ('done', 'Done'), ('returned', 'Returned')],
        string='State', required=True, default='draft', tracking=True)


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('alifzerocms.documents', 'doc_attach_rel', 'attach_id', 'doc_id',
                                      string="Attachment", invisible=1)


class DocumentDocument(models.Model):
    _name = 'document.document'
    _description = "Documents Type"

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')
