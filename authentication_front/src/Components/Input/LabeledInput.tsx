import React from "react";
import styles from "./Input.module.scss";
import Input from "./Input";

interface Props {
    type: "text" | "password";
    label: string;
    placeHolder: string;
    value: string | undefined;
    setValue: (initialState: string) => void;
    errored: boolean;
}

const LabeledInput: React.FC<Props> = ({
    type,
    label,
    placeHolder,
    setValue,
    value,
    errored = false,
}) => {
    return (
        <label className={styles.label}>
            <span className={styles.labelText}>{label}</span>
            <Input
                errored={errored}
                value={value}
                type={type}
                placeHolder={placeHolder}
                setValue={setValue}
            />
        </label>
    );
};

export default LabeledInput;
