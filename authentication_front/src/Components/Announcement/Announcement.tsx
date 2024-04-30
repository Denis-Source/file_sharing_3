import React from "react";
import Ghost, {Animations} from "../Ghost/Ghost";
import styles from "./Announcement.module.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    animation: Animations;
    header: string;
    description: string | undefined;
}

const Announcement: React.FC<Props> = ({animation, header, description, ...restProps}) => {
    return (
        <div className={styles.container} {...restProps}>
            <div className={restProps.onClick ? styles.ghostClickable : styles.ghost}>
                <Ghost animation={animation} />
                <h2 className={styles.header}>{header}</h2>
                {description && (
                    <div className={styles.descriptionContainer}>
                        <p>{description}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Announcement;
