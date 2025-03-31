/** @odoo-module **/

import {Component, useRef} from "@odoo/owl";

import {TranslationButton} from "@web/views/fields/translation_button";
import {_t} from "@web/core/l10n/translation";
import {formatChar} from "@web/views/fields/formatters";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useInputField} from "@web/views/fields/input_field_hook";

export class EncryptedField extends Component {
    static template = "web.EncryptedField";
    static components = {
        TranslationButton,
    };
    static props = {
        ...standardFieldProps,
        placeholder: {type: String, optional: true},
    };
    static defaultProps = {};

    setup() {
        this.input = useRef("input");
        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
            parse: (v) => this.parse(v),
        });
    }

    get maxLength() {
        return this.props.record.fields[this.props.name].size;
    }

    get formattedValue() {
        return formatChar(this.props.record.data[this.props.name], {});
    }

    parse(value) {
        return value;
    }
}

export const encryptedField = {
    component: EncryptedField,
    displayName: _t("Text"),
    supportedTypes: ["encrypted"],
    supportedOptions: [],
    extractProps: ({attrs}) => ({
        placeholder: attrs.placeholder,
    }),
};

registry.category("fields").add("encrypted", encryptedField);
