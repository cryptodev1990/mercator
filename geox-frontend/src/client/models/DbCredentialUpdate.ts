/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type DbCredentialUpdate = {
    id: string;
    name?: string;
    should_delete?: boolean;
    is_default?: boolean;
    db_user?: string;
    db_password?: string;
    db_host?: string;
    db_port?: string;
    db_database?: string;
    db_extras?: any;
    db_driver?: string;
};

