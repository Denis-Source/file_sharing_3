import React, {ReactNode} from "react";
import styles from "./BaseLayout.module.scss";

interface Props {
    children?: ReactNode | ReactNode[];
}

const BaseLayout: React.FC<Props> = ({children}) => {
    return (
        <>
            <div className={styles.background}/>
            <div className={styles.container}>
                {children}
            </div>
        </>
    );
};

export default BaseLayout;
