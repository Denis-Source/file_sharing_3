import React from "react";
import Ghost, {Animations} from "../Ghost/Ghost";
import styles from "./Announcement.module.scss";

interface Props {
    animation: Animations;
    header: string;
    description: string | undefined;
    onClick?: () => void;
}

const Announcement: React.FC<Props> = ({animation, header, description, onClick}) => {
    return (
        <div className={styles.container} onClick={onClick}>
            <div className={onClick ? styles.ghostClickable : styles.ghost}>
                <Ghost animation={animation}/>
                <h2 className={styles.header}>{header}</h2>
                {description && (
                    <div className={styles.descriptionContainer}>
                        <p className={styles.description}>{description}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Announcement;
