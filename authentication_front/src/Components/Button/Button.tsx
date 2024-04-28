import React from "react";
import styles from "./Button.module.scss";
import {Strings} from "./Strings";

interface Props {
    text?: string;
    onClick?: () => void;
}

const Button: React.FC<Props> = ({text, onClick}) => {
    return (
        <button className={styles.button} onSubmit={onClick}>
            {text ? text : Strings.Submit}
        </button>
    );
};

export default Button;
