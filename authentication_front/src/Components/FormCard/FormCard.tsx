import React, {FormEvent, useEffect, useState} from "react";
import styles from "./FormCard.module.scss";

interface Props extends React.HTMLAttributes<HTMLFormElement> {
    onSubmit: (event: FormEvent) => void;
    message: string | null;
    errored?: boolean;
    header?: string;
}

const FormCard: React.FC<Props> = ({message, header, errored = false, ...restProps}) => {
    const [shaken, setShaken] = useState<boolean>(Boolean(errored));
    useEffect(() => {
        message && setShaken(true);
        setInterval(() => setShaken(false), 200);
    }, [errored, message]);

    return (
        <div className={shaken ? styles.containerShake : styles.container}>
            <div className={styles.headerContainer}>
                {header && <h1 className={styles.header}>{header}</h1>}
                <span className={styles.errorMessage}>{message}</span>
            </div>
            <form className={styles.form} {...restProps} />
        </div>
    );
};

export default FormCard;
