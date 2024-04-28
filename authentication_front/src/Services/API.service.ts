import queryString from "query-string";

export const getAPIUrl = (): string => {
    return "http://127.0.0.1:8000/";
};

const capitalizeString = (string: string): string => {
    return string.charAt(0).toUpperCase() + string.slice(1);
};

export class APIError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "APIError";
    }
}

export const fetchAPI = async (
    path: string,
    options: RequestInit,
    params?: object
): Promise<any> => {
    options = {
        headers: {
            "Content-Type": "application/json",
        },
        ...options,
    };
    let url = `${getAPIUrl()}${path}`;
    if (params) {
        url += `?${queryString.stringify(params)}`
    }

    const response = await fetch(url, options);
    if (response.ok) {
        return response;
    } else {
        let message: string | any = Object.values(await response.json())[0];
        if (message instanceof Array) {
            message = message[0] as string;
        }
        message = capitalizeString(message.toLowerCase());
        throw new APIError(message);
    }
};

export const fetchAPIJSON = async (
    path: string,
    method: "GET" | "POST" | "PUT" | "DELETE",
    body?: object,
    params?: object,
): Promise<any> => {
    const options = {
        method: method,
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json",
        },
        mode: "cors" as RequestMode,
    };
    return await fetchAPI(path, options, params);
};