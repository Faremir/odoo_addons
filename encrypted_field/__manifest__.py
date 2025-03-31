# pylama:ignore=C0114,D100
{
    "name": "Encrypted Field",
    "summary": "Introduces an Encrypted field type for secure data storage.",
    "author": "Jiri Blahut <j.faremir.b@gmail.com>",
    "website": "https://github.com/Faremir/odoo_addons",
    "license": "AGPL-3",
    "version": "17.0.0.0.1",
    "category": "Hidden/Tools",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        # Core Modules
        "base",
        "web",
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "encrypted_field/static/src/views/fields/encrypted/encrypted_field.esm.js",
        ],
        "web.qunit_suite_tests": [
            "encrypted_field/static/tests/views/fields/encrypted_field_tests.js",
        ],
    },
    "external_dependencies": {
        "python": ["cryptography"],
    },
}
