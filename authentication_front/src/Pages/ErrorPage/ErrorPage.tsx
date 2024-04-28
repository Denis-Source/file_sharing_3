import React from "react";
import Announcement from "../../Components/Announcement/Announcement";
import {Animations} from "../../Components/Ghost/Ghost";
import CenteredLayout from "../../Layouts/CenteredLayout/CenteredLayout";

interface Props {
    message: string;
    description: string | undefined;
}

const ErrorPage: React.FC<Props> = (
    {
        message,
        description
    }) => {
    return (
        <CenteredLayout>
            <Announcement
                animation={Animations.Shake}
                header={message}
                description={description}
            />
        </CenteredLayout>
    );
};

export default ErrorPage;
