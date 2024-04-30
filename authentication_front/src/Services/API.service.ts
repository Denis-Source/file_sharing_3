import queryString from "query-string";

export const getAPIUrl = (): string => {
    return "http://127.0.0.1:8000/";
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
    if (params) url += `?${queryString.stringify(params)}`
    let response;
    try {
        response = await fetch(url, options);
    } catch (e) {
        throw new APIError("Some error occurred!")
    }
    if (response.ok) return response;
    const {detail} = await response.json();
    throw new APIError(detail);
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