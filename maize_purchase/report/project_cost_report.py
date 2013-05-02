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

class project_cost_report(osv.osv):
    _name = "project.cost.report"
    _description = "Project Cost Analysis"
    _auto = False

    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'PO Number', readonly=True),
        'indent_id': fields.many2one('indent.indent', 'Indent', readonly=True),
        'indentor_id': fields.many2one('res.users', 'Indentor', readonly=True),
        'project_code': fields.char('Project Code',size=28),
        'project_name': fields.char('Project Name', size=256),
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
        'price_unit': fields.float('Rate', readonly=True),
        'contract': fields.boolean('Contract'),
        'puchase_total': fields.float('PO Value', readonly=True),
        'receipt_total': fields.float('Receipt', readonly=True),
        'payment': fields.float('Payment', readonly=True),
        'difference': fields.float('Difference', readonly=True),
    }
    _order = 'puchase_total desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'project_cost_report')
        cr.execute("""
            create or replace view project_cost_report as (
                select
                    min(po.id) as id,
                    i.id as indent_id,
                    po.id as purchase_id,
                    i.contract as contract,
                    l.price_unit as price_unit,
                    sum(l.product_qty * l.price_unit) as price_total,
                    po.partner_id as partner_id,
                    po.amount_total as puchase_total,
                    sp.amount_total as receipt_total,
                    a.name as project_name,
                    a.code as project_code,
                    sum(sp.amount_total - 0) as difference,
                    1 as nbr,
                    i.indentor_id as indentor_id,
                    i.state,
                    i.analytic_account_id as analytic_account_id
                from
                    indent_indent i
                    left join purchase_order po on (i.id=po.indent_id)
                    left join purchase_order_line l on (l.order_id = po.id)
                    left join product_product p on (l.product_id=p.id)
                    left join product_template t on (p.product_tmpl_id=t.id)
                    left join stock_picking sp on (po.id = sp.purchase_id)
                    left join account_analytic_account a on (i.analytic_account_id = a.id)
                where po.indent_id is not null and l.product_id is not null and sp.type in ('out', 'in', 'receipt')
                group by
                    po.id,
                    i.id,
                    i.contract,
                    po.amount_total,
                    i.indentor_id,
                    i.state,
                    i.analytic_account_id,
                    l.product_qty,
                    l.price_unit,
                    po.partner_id,
                    i.analytic_account_id,
                    sp.amount_total,
                    a.name,
                    a.code
            )
        """)
project_cost_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
