import {createBrowserRouter} from "react-router-dom";
import ErrorPage from "./Pages/ErrorPage/ErrorPage";
import {Strings} from "./strings";
import LoginPage from "./Pages/LoginPage/LoginPage";

export enum RouterPaths {
    Login = "/login",
    Error = "/error",
}

export const router = createBrowserRouter([
    {
        path: RouterPaths.Login,
        element: <LoginPage />,
    },
    {
        path: RouterPaths.Error,
        element: (
            <ErrorPage
                message={Strings.GenericErrorMessage}
                description={Strings.GenericErrorDescription}
            />
        ),
    },
    {
        path: "*",
        element: (
            <ErrorPage
                message={Strings.NoPageFoundMessage}
                description={Strings.NoPageFoundDescription}
            />
        ),
    },
]);
