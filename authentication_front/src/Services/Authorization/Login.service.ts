import {fetchAPIJSON} from "../API.service";

export const LOGIN_URL = "auth/login-code/";

export interface LoginDTO {
    username: string;
    password: string;
}

export interface RedirectDTO {
    redirect_uri: string;
}

export const login = async (
    body: LoginDTO,
    clientID: number,
    redirectURI: string
): Promise<RedirectDTO> => {
    const params = {
        client_id: clientID,
        redirect_uri: redirectURI,
    };
    const response = await fetchAPIJSON(LOGIN_URL, "POST", body, params);
    return await response.json();
};
