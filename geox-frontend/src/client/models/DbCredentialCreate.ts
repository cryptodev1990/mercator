/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type DbCredentialCreate = {
    /**
     * Name of the connection
     */
    name: string;
    /**
     * Makes connection the default for publishing
     */
    is_default?: boolean;
    db_user: string;
    db_password: string;
    db_host: string;
    db_port: string;
    db_database: string;
    db_driver: string;
    db_extras?: any;
};

