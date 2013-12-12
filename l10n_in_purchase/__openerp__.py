# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2013 Tiny SPRL (<http://tiny.be>).
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
{
    'name' : 'l10n_in_purchase',
    'version' : '0.1',
    'author' : 'OpenERP S.A.',
    'sequence': 111,
    'category': 'Purchase Management',
    'website' : 'http://www.openerp.com',
    'summary' : 'Purchase Management, Indian localization',
    'description' : """
Manage Freight, Packaging & Forwarding, Insurance, Mill Delivery
=====================================================================
This module allows you to manage different charges on Purchase orders & Supplier invoices used for Indian Localization.

* Freight
* Packaging & Forwarding
* Insurance
* Mill Delivery

Management of Rates and Amounts
++++++++++++++++++++++++++++++++++++++
You can manage calculation of various charges by different applicable options.

* **Fix Amount**: Fix amount applicable on total price
* **Percentage**: Amount in percentage applicable on total price
* **Per Unit**: Fix amount applicable per unit on total quantity of items
* **At actual**: Charge different rates over time
* **Include in Price**: Recomputes price of items to adjust amount in price of items

Reports
++++++++++
It also prints reports of Purchase orders and Supplier Invoices with Freight/Packaging etc. information.
""",
    'depends' : ['purchase'],
    'data' : [
    ],
    'update_xml' : ['l10n_in_purchase_view.xml',
                    'l10n_in_account_view.xml',
                    'purchase_report.xml',
    ],

    'demo': [],

    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
