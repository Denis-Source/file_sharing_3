import React, {FormEvent, ReactNode} from "react";
import styles from "./FormCard.module.scss";

interface Props {
    onSubmit: (event: FormEvent) => void;
    errored: boolean;
    errorMessage?: string;
    header?: string;
    children?: ReactNode | ReactNode[];
}

const FormCard: React.FC<Props> = (
    {
        onSubmit,
        errored,
        errorMessage,
        header,
        children
    }) => {
    return (
        <div className={errored ? styles.containerShake : styles.container}>
            <div className={styles.headerContainer}>
                {header && <h1 className={styles.header}>{header}</h1>}
                <span className={styles.errorMessage}>{errorMessage}</span>
            </div>
            <form className={styles.form} onSubmit={onSubmit}>
                {children}
            </form>
        </div>
    );
};

export default FormCard;
