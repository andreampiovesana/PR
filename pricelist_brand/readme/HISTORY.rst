20.0.1.0.0 (2026-09-19)
~~~~~~~~~~~~~~~~~~~~~~~

* [MIG] Migration to Odoo 20.0
* ``applied_on`` is a computed stored field in 20.0: ``_compute_applied_on`` is extended
  instead of normalizing the rule target in ``create``/``write``, and the
  ``display_applied_on`` field it used to rely on no longer exists
* ``odoo.osv.expression`` was removed: the applicable-rules domain now uses
  ``odoo.fields.Domain``
* ``_get_applicable_rules_domain`` takes ``date``/``quantity``/``uom`` as keyword-only
  arguments and returns a ``Domain``
* ``_compute_name`` follows the core 20.0 wording and shows the brand display name
  without a ``Brand:`` prefix
* ``applied_on`` has no default any more, so the ``25_brand`` ondelete policy went from
  ``set default`` to ``set 3_global``
* ``static/description/index.html``: dropped the XML declaration, which breaks the
  module description parser in 20.0 (newer ``oca-gen-addon-readme`` output no longer
  emits it)
