import React, {FormEvent, useEffect, useState} from "react";
import {PASSWORD_REGEX, USERNAME_REGEX} from "./Regex";
import {login} from "../../Services/Authorization/Login.service";
import {useNavigate, useSearchParams} from "react-router-dom";
import {APIError} from "../../Services/API.service";
import Spinner from "../../Components/Spinner/Spinner";
import FormCard from "../../Components/FormCard/FormCard";
import Input from "../../Components/Input/Input";
import Button from "../../Components/Button/Button";
import {RouterPaths} from "../../router";

interface FormState {
    username: string
    password: string
    message: string | null
    errored: boolean
}

const initialFormState: FormState = {
    username: "",
    password: "",
    message: null,
    errored: false
}

interface QsState {
    clientID: number | null
    redirectURI: string | null
    loaded: boolean
}

const initialQsState: QsState = {
    clientID: null,
    redirectURI: null,
    loaded: false
}

enum Strings {
    Header = "Header",

    UsernameInvalidated = "Incorrect username",
    UsernameLabel = "Username",
    UsernamePlaceholder = "Example",

    PasswordInvalidated = "Incorrect password",
    PasswordLabel = "Password",
    PasswordPlaceholder = "••••••••"
}

const LoginContainer = () => {
    const [formState, setFormState] = useState<FormState>(initialFormState);
    const [qsState, setQsState] = useState<QsState>(initialQsState)
    const [loading, setLoading] = useState<boolean>(false)

    const [params, setParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {
        params.get("client_id") && setQsState(prevState =>
            ({...prevState, clientID: Number(params.get("client_id"))}))
        params.get("redirect_uri") && setQsState(prevState =>
            ({...prevState, redirectURI: params.get("redirect_uri")}))
        setQsState(prevState =>
            ({...prevState, loaded: true}))
        setParams({})
    }, [qsState.clientID, qsState.redirectURI, setQsState, params, setParams])

    useEffect(() => {
        if (!qsState.loaded) return
        if (qsState.redirectURI || qsState.clientID) return;
        navigate(RouterPaths.Error)
    }, [qsState, navigate, setParams])

    const validateForm = () => {
        PASSWORD_REGEX.test(formState.password)
            ? setFormState(prevState => ({...prevState, errored: false}))
            : setFormState(prevState => ({...prevState, message: Strings.UsernameInvalidated, errored: true}))
        USERNAME_REGEX.test(formState.username)
            ? setFormState(prevState => ({...prevState, errored: false}))
            : setFormState(prevState => ({...prevState, message: Strings.PasswordInvalidated, errored: true}))
    }

    const onSubmit = async (event: FormEvent) => {
        event.preventDefault();

        validateForm()
        if (formState.errored) return;
        if (!formState.username || !formState.password) return;
        if (!qsState.clientID || !qsState.redirectURI) return;

        setFormState(prevState => ({...prevState, message: null}))
        setLoading(true);

        try {
            const {redirect_uri} = await login(
                {
                    username: formState.username,
                    password: formState.password
                },
                qsState.clientID,
                qsState.redirectURI);
            window.location.href = redirect_uri
        } catch (e: any) {
            (e instanceof APIError)
            && setFormState(prevState => ({...prevState, message: e.message}))
        }
        setLoading(false)
    };

    return (
        <>
            {loading ?
                <Spinner/> :
                <FormCard
                    onSubmit={onSubmit}
                    message={formState.message}
                    errored={!!formState.message || formState.errored}
                    header={Strings.Header}>
                    <Input
                        type={"text"}
                        label={Strings.UsernameLabel}
                        placeholder={Strings.UsernamePlaceholder}
                        value={formState.username}
                        setValue={(value) => setFormState(prevState => ({...prevState, username: value}))}/>
                    <Input
                        type={"password"}
                        label={Strings.PasswordLabel}
                        placeholder={Strings.PasswordPlaceholder}
                        value={formState.password}
                        setValue={(value) => setFormState(prevState => ({...prevState, password: value}))}/>
                    <Button/>
                </FormCard>
            }
        </>
    );
};

export default LoginContainer;
