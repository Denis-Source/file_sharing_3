import React, {useEffect, useState} from "react";
import {APIError} from "../../Services/API.service";
import {useNavigate, useSearchParams} from "react-router-dom";
import LoginContainer from "../../Containers/LoginContainer/LoginContainer";
import {login, LoginDTO} from "../../Services/Authorization/Login.service";
import CenteredLayout from "../../Layouts/CenteredLayout/CenteredLayout";
import {RouterPaths} from "../../router";


const LoginPage = () => {
        const [errorMessage, setErrorMessage] = useState<string>("");
        const [formData, setFormData] = useState<LoginDTO | null>(null);
        const [errored, setErrored] = useState<boolean>(false);
        const [params, setParams] = useSearchParams();
        const [clientID, setClientID] = useState<number | null>(null)
        const [redirectURI, setRedirectURI] = useState<string | null>(null)
        const [paramsLoaded, setParamsLoaded] = useState<boolean>(false)

        const navigate = useNavigate();

        useEffect(() => {
            params.get("client_id") && setClientID(Number(params.get("client_id")));
            params.get("redirect_uri") && setRedirectURI(params.get("redirect_uri"));
            setParamsLoaded(true)
            setParams({})
        }, [clientID, setClientID, redirectURI, setRedirectURI, params, setParams])

        console.log(clientID)
        console.log(redirectURI)

        useEffect(() => {
                const loginUser = async () => {
                    if (!paramsLoaded) {
                        return
                    }
                    if (!redirectURI || !clientID) {
                        navigate(RouterPaths.Error)
                        return
                    }
                    if (!formData) {
                        return
                    }
                    try {
                        const {redirect_uri} = await login(formData, clientID, redirectURI);
                        window.location.href = redirect_uri
                    } catch (e) {
                        if (e instanceof APIError) {
                            setErrored(true);
                            setErrorMessage(e.message);
                        }
                    }
                };
                loginUser().then();
            }, [formData, navigate, clientID, redirectURI, paramsLoaded]
        )
        ;

        return (
            <CenteredLayout>
                <LoginContainer
                    errorMessage={errorMessage}
                    errored={errored}
                    setErrored={setErrored}
                    formData={formData}
                    setFormData={setFormData}
                />
            </CenteredLayout>
        );
    }
;

export default LoginPage;
