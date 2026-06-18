# Copyright 2026 Nextev Srl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    """Mark l10n_it_stock_ddt for uninstallation if it was auto-installed."""
    IrModule = env["ir.module.module"]
    l10n_it_stock_ddt = IrModule.search(
        [
            ("name", "=", "l10n_it_stock_ddt"),
            ("state", "in", ["installed", "to upgrade"]),
        ]
    )
    if l10n_it_stock_ddt:
        l10n_it_stock_ddt.button_uninstall()
