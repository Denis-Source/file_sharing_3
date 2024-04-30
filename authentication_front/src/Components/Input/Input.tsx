import React from "react";
import styles from "./Input.module.scss";

interface Props extends React.InputHTMLAttributes<HTMLInputElement> {
    label: string;
    setValue: (value: string) => void;
    shadowed?: boolean;
}

const Input: React.FC<Props> = (
    {
        label,
        setValue,
        shadowed = false,
        ...restProps
    }) => {
    return (
        <label className={styles.label}>
            <span className={styles.labelText}>{label}</span>
            <input
                className={shadowed ? styles.inputShadowed : styles.input}
                onChange={event => setValue(event.target.value)}
                {...restProps}
            />
        </label>
    );
};

export default Input;
