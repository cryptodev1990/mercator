/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type PublicDbCredential = {
    id: string;
    name: string;
    is_default?: boolean;
    created_at: string;
    created_by_user_id: number;
    updated_at: string;
    updated_by_user_id: number;
    organization_id?: string;
    db_driver: string;
};

