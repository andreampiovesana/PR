# Copyright 2026 Nextev Srl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "ITA - Fatturazione Elettronica - Documento di Trasporto",
    "summary": "Dati DDT in fatture elettroniche",
    "version": "18.0.1.0.0",
    "category": "Localization/Italy",
    "website": "https://github.com/OCA/l10n-italy",
    "author": "Nextev Srl, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "l10n_it_edi",
        "l10n_it_delivery_note",
    ],
    "data": [
        "data/l10n_it_edi_delivery_note_template.xml",
    ],
    "excludes": ["l10n_it_stock_ddt"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
