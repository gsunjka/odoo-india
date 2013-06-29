# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class indent_report(osv.osv):
    _name = "indent.report"
    _description = "Indent Statistics"
    _auto = False

    def amount_tax(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'pending_value':0.0,
            }
            res[order.id]['pending_value'] = ( order.price_unit  *order.pending_qty)
        return res

    _columns = {
        'name': fields.char('Indent #', size=256, readonly=True),
        'indent_maize_id': fields.char('Maize Indent', size=256),
        'date': fields.date('Indent Date', readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'contract': fields.boolean('Contract'),
        'department_id': fields.many2one('stock.location', 'Department', readonly=True),
        'requirement': fields.selection([('ordinary','Ordinary'), ('urgent','Urgent')], 'Requirement', readonly=True),
        'required_date': fields.date('Required Date', readonly=True),
        'type': fields.selection([('new','New'), ('existing','Existing')], 'Type', readonly=True),
        'item_for': fields.selection([('store', 'Store'), ('capital', 'Capital')], 'Item For', readonly=True),
        'purpose': fields.text('Purpose', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'product_code': fields.char('Product Code', size=64, readonly=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', readonly=True),
        'product_uom_qty': fields.float('# of Qty', readonly=True),
        'indent_id': fields.many2one('indent.indent', 'Indent', readonly=True),
        'indentor_id': fields.many2one('res.users', 'Indentor', readonly=True),
        'price_unit': fields.float('Rate', readonly=True),
        'price_total': fields.float('Value', readonly=True),
        'nbr': fields.integer('# of Lines', readonly=True),
        'state':fields.selection([
            ('draft','Draft'),
            ('confirm','Confirm'),
            ('waiting_approval','Waiting For Approval'),
            ('inprogress','Inprogress'),
            ('received','Received'),
            ('reject','Rejected')
            ], 'State', readonly=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Project', readonly=True),
        'days': fields.integer("Days", help="Calculate number of days for contracts"),
        'extend_days1': fields.integer("Extend Days1", help="Calculate Extended number of days 1st time for contracts"),
        'extend_days2': fields.integer("Extend Days2", help="Calculate Extended number of days 2nd time for contracts"),
        'total_days': fields.integer("Total Days", help="Calculate number of days for contracts"),
        'purchase_date': fields.date('Purchase Date', readonly=True),
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True),
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order', readonly=True),
        'pending_qty': fields.float('Pending Qty', readonly=True),
        'pending_value': fields.function(amount_tax, digits_compute= dp.get_precision('Account'), string='Pending Value', type="float", multi="tax",help="Pending Value"),
        'remark': fields.text('Remark', readonly=True),
    }
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'indent_report')
        cr.execute("""
            create or replace view indent_report as (
                select
                    min(l.id) as id,
                    i.id as indent_id,
                    i.name as name,
                    i.maize as indent_maize_id,
                    i.contract as contract,
                    i.department_id as department_id,
                    i.requirement as requirement,
                    i.required_date as required_date,
                    i.type as type,
                    i.item_for as item_for,
                    l.name as purpose,
                    l.product_id as product_id,
                    p.default_code as product_code,
                    t.uom_id as product_uom,
                    l.product_uom_qty as product_uom_qty,
                    l.price_unit as price_unit,
                    min(l.product_uom_qty * l.price_unit) as price_total,
                    1 as nbr,
                    i.indent_date as date,
                    to_char(i.indent_date, 'YYYY') as year,
                    to_char(i.indent_date, 'MM') as month,
                    to_char(i.indent_date, 'YYYY-MM-DD') as day,
                    i.indentor_id as indentor_id,
                    i.state,
                    i.analytic_account_id as analytic_account_id,
                    i.description as remark,
                    po.date_order as purchase_date,
                    po.partner_id as supplier_id,
                    po.id as purchase_id,
                    CASE WHEN po.state = 'draft' or sm.state != 'done' or po.contract = True THEN
                        sum(l.product_uom_qty)
                    ELSE
                        l.product_uom_qty - sum(sm.product_qty)
                    END AS pending_qty,
                    po.no_of_days1 as days,
                    po.total_days as total_days,
                    po.no_of_days2 as extend_days1,
                    po.no_of_days3 as extend_days2
                from
                    indent_indent i
                    left join indent_product_lines l on (i.id=l.indent_id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join stock_location sl on (sl.id=i.department_id)
                    left join purchase_order po on (po.indent_id = i.id)
                    left join stock_move sm on (sm.indent=i.id and sm.type='receipt' and sm.product_id=p.id)
                where l.product_id is not null
                group by
                    i.id,
                    i.name,
                    i.contract,
                    i.department_id,
                    i.requirement,
                    i.required_date,
                    i.description,
                    i.type,
                    i.item_for,
                    l.name,
                    l.product_id,
                    p.default_code,
                    l.product_uom_qty,
                    l.price_unit,
                    l.indent_id,
                    t.uom_id,
                    i.indent_date,
                    i.indentor_id,
                    i.state,
                    i.analytic_account_id,
                    i.maize,
                    po.date_order,
                    po.partner_id,
                    po.id,
                    po.no_of_days1,
                    po.no_of_days2,
                    po.no_of_days3,
                    po.total_days,
                    sm.state,
                    po.contract,
                    l.product_uom_qty
            )
        """)
indent_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
