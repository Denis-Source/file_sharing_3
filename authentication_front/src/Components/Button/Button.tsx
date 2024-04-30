import React from "react";
import styles from "./Button.module.scss";


interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    text?: string;
}

enum Strings {
    Submit = "Submit",
}


const Button: React.FC<Props> = (
    {
        text,
        ...restProps
    }) => {
    return (
        <button
            className={styles.button}
            {...restProps}>
            {text ? text : Strings.Submit}
        </button>
    );
};

export default Button;
