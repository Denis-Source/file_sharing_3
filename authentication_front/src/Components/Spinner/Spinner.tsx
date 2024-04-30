import React from "react";

import styles from "./Spinner.module.scss";
import spinner from "./Spinner.svg";

enum Strings {
    SpinnerAlt = "SpinnerLayout",
}

const Spinner = () => {
    return (
        <div className={styles.container}>
            <div className={styles.shadow}>
                <img className={styles.icon} src={spinner} alt={Strings.SpinnerAlt} />
            </div>
        </div>
    );
};

export default Spinner;
