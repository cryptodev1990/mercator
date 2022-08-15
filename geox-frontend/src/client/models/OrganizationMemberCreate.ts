/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type OrganizationMemberCreate = {
    organization_id: string;
    user_id: number;
    has_read?: boolean;
    has_write?: boolean;
    is_admin?: boolean;
};

