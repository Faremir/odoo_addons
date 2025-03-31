/** @odoo-module **/

import {click, clickSave, editInput, getFixture} from "@web/../tests/helpers/utils";
import {makeView, setupViewRegistries} from "@web/../tests/views/helpers";

// eslint-disable-next-line init-declarations
let serverData;
// eslint-disable-next-line init-declarations
let target;

// eslint-disable-next-line no-undef
QUnit.module("Fields", (hooks) => {
    hooks.beforeEach(() => {
        target = getFixture();
        serverData = {
            models: {
                partner: {
                    fields: {
                        encrypted: {string: "Binary", type: "encrypted"},
                    },
                    records: [
                        {
                            encrypted: "12345",
                        },
                    ],
                },
            },
        };

        setupViewRegistries();
    });

    // eslint-disable-next-line no-undef
    QUnit.module("EncryptedField");

    // eslint-disable-next-line no-undef
    QUnit.test("EncryptedField in form view", async function (assert) {
        await makeView({
            serverData,
            type: "form",
            resModel: "partner",
            arch: `
                <form>
                    <sheet>
                        <group>
                            <field name="encrypted" />
                        </group>
                    </sheet>
                </form>`,
            resId: 1,
        });
        assert.containsOnce(
            target,
            ".o_field_widget input[type='password']",
            "should have an input for the ecrypted field"
        );
        assert.strictEqual(
            target.querySelector(".o_field_widget input[type='password']").value,
            "12345",
            "input should contain field value in edit mode"
        );
        // Change value in edit mode
        await editInput(target, ".o_field_widget input[type='password']", "limbo");

        // Save
        await clickSave(target);
        assert.strictEqual(
            target.querySelector(".o_field_widget input[type='password']").value,
            "limbo",
            "the new value should be displayed"
        );
    });

    // eslint-disable-next-line no-undef
    QUnit.test(
        "setting a encrypted field to empty string is saved as a false value",
        async function (assert) {
            assert.expect(1);

            await makeView({
                type: "form",
                resModel: "partner",
                serverData,
                arch: `
                <form>
                    <sheet>
                        <group>
                            <field name="encrypted" />
                        </group>
                    </sheet>
                </form>`,
                resId: 1,
                mockRPC(route, {args, method}) {
                    if (method === "web_save") {
                        assert.strictEqual(
                            args[1].encrypted,
                            false,
                            "the encrypted value should be false"
                        );
                    }
                },
            });

            await editInput(target, ".o_field_widget input[type='password']", "");
            await clickSave(target);
        }
    );

    // eslint-disable-next-line no-undef
    QUnit.test("char field in editable list view", async function (assert) {
        await makeView({
            type: "list",
            resModel: "partner",
            serverData,
            arch: `
                <tree editable="bottom">
                    <field name="encrypted"/>
                </tree>`,
        });

        assert.containsN(
            target,
            "tbody td:not(.o_list_record_selector)",
            5,
            "should have 5 cells"
        );
        assert.strictEqual(
            target.querySelector("tbody td:not(.o_list_record_selector)").textContent,
            "",
            "textContent should be empty"
        );

        // Edit a line and check the result
        let cell = target.querySelector("tbody td:not(.o_list_record_selector)");
        await click(cell);
        assert.hasClass(
            cell.parentElement,
            "o_selected_row",
            "should be set as edit mode"
        );
        assert.strictEqual(
            cell.querySelector("input").value,
            "yop",
            "should have the correct value in internal input"
        );

        await editInput(cell, "input", "brolo");

        // Save
        await clickSave(target);
        cell = target.querySelector("tbody td:not(.o_list_record_selector)");
        assert.doesNotHaveClass(
            cell.parentElement,
            "o_selected_row",
            "should not be in edit mode anymore"
        );
        assert.strictEqual(
            target.querySelector("tbody td:not(.o_list_record_selector)").textContent,
            "brolo",
            "value should be properly updated"
        );
    });
});
