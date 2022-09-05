/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type UserWithMembership = {
    email: string;
    id: number;
    sub_id: string;
    given_name?: string;
    family_name?: string;
    nickname?: string;
    name?: string;
    locale?: string;
    picture?: string;
    last_login_at?: string;
    is_active: boolean;
    organization_id: string;
    is_personal: boolean;
};

