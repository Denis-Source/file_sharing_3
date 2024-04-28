import React, {ReactNode} from "react";
import styles from "./CenteredLayout.module.scss";
import BaseLayout from "../BaseLayout/BaseLayout";

interface Props {
    children?: ReactNode | ReactNode[];
}

const CenteredLayout: React.FC<Props> = ({children}) => {
    return (
        <BaseLayout>
            <div className={styles.container}>
                {children}
            </div>
        </BaseLayout>
    );
};

export default CenteredLayout;
