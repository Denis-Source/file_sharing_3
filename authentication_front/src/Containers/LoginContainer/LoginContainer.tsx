import React, {FormEvent, useEffect, useState} from "react";
import FormCard from "../../Components/FormCard/FormCard";
import LabeledInput from "../../Components/Input/LabeledInput";
import Button from "../../Components/Button/Button";
import {LoginDTO} from "../../Services/Authorization/Login.service";
import {PASSWORD_REGEX, USERNAME_REGEX} from "./Regex";

interface Props {
    errored: boolean;
    setErrored: (initialState: boolean) => void;
    errorMessage: string;
    setErrorMessage: (initialState: string) => void;
    formData: LoginDTO | null;
    setFormData: (initialState: LoginDTO) => void;
}

const LoginContainer: React.FC<Props> = (
    {
        errored,
        setErrored,
        errorMessage,
        setErrorMessage,
        formData,
        setFormData,
    }) => {
    const [username, setUsername] = useState<string>(
        formData?.username ? formData.username : ""
    );
    const [password, setPassword] = useState<string>(
        formData?.password ? formData.password : ""
    );

    const [usernameErrored, setUsernameErrored] = useState<boolean>(false);
    const [passwordErrored, setPasswordErrored] = useState<boolean>(false);

    useEffect(() => {
        if (!username) return
        USERNAME_REGEX.test(username) ? setUsernameErrored(false) : setUsernameErrored(true);

    }, [username]);

    useEffect(() => {
        if (!password) return
        PASSWORD_REGEX.test(password) ? setPasswordErrored(false) : setPasswordErrored(true);
    }, [password]);

    const onSubmit = (event: FormEvent) => {
        event.preventDefault();
        setErrored(false);
        if (password && !passwordErrored && username && !usernameErrored) {
            setFormData({
                username: username,
                password: password,
            });
        } else {
            setErrored(true);
            setTimeout(
                () => {
                    setErrored(false);
                    setErrorMessage("Incorrect inputs");
                },
                100
            )
        }
    };

    return (
        <FormCard
            onSubmit={onSubmit}
            errored={errored}
            errorMessage={errorMessage}
            header={"Sign In"}
        >
            <LabeledInput
                errored={usernameErrored}
                type={"text"}
                label={"Username"}
                placeHolder={"Example"}
                value={username}
                setValue={setUsername}
            />
            <LabeledInput
                errored={passwordErrored}
                type={"password"}
                label={"Password"}
                placeHolder={"••••••••"}
                value={password}
                setValue={setPassword}
            />
            <Button/>
        </FormCard>
    );
};

export default LoginContainer;
