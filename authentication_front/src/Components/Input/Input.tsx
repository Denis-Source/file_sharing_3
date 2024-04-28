import React from "react";
import styles from "./Input.module.scss";

interface Props {
    type: "text" | "password";
    placeHolder: string;
    value: string | undefined;
    setValue: (initialState: string) => void;
    errored?: boolean;
    shadowed?: boolean;
}

const Input: React.FC<Props> = ({
    type,
    placeHolder,
    setValue,
    value,
    errored = false,
    shadowed = false,
}) => {
    return (
        <input
            placeholder={placeHolder}
            className={
                shadowed ? styles.inputShadowed : errored ? styles.inputErrored : styles.input
            }
            type={type}
            value={value}
            onChange={event => setValue(event.target.value)}
        />
    );
};

export default Input;
