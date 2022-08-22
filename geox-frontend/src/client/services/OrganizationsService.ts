/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Organization } from "../models/Organization";
import type { OrganizationCreate } from "../models/OrganizationCreate";
import type { OrganizationMemberCreate } from "../models/OrganizationMemberCreate";
import type { OrganizationMemberDelete } from "../models/OrganizationMemberDelete";
import type { OrganizationMemberUpdate } from "../models/OrganizationMemberUpdate";
import type { OrganizationUpdate } from "../models/OrganizationUpdate";
import type { UserWithMembership } from "../models/UserWithMembership";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class OrganizationsService {
  /**
   * Get Organizations
   * @returns Organization Successful Response
   * @throws ApiError
   */
  public static getOrganizationsOrganizationsGet(): CancelablePromise<
    Array<Organization>
  > {
    return __request(OpenAPI, {
      method: "GET",
      url: "/organizations",
    });
  }

  /**
   * Create Organization
   * @param requestBody
   * @returns UserWithMembership Successful Response
   * @throws ApiError
   */
  public static createOrganizationOrganizationsPost(
    requestBody: OrganizationCreate
  ): CancelablePromise<UserWithMembership> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/organizations",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Active Org
   * @returns Organization Successful Response
   * @throws ApiError
   */
  public static getActiveOrgOrganizationsActiveGet(): CancelablePromise<Organization> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/organizations/active",
    });
  }

  /**
   * Set Active Org
   * @param organizationUuid
   * @returns Organization Successful Response
   * @throws ApiError
   */
  public static setActiveOrgOrganizationsActivePost(
    organizationUuid: string
  ): CancelablePromise<Organization> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/organizations/active",
      query: {
        organization_uuid: organizationUuid,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Organization
   * @param organizationId
   * @returns Organization Successful Response
   * @throws ApiError
   */
  public static getOrganizationOrganizationsOrganizationIdGet(
    organizationId: string
  ): CancelablePromise<Organization> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/organizations/{organization_id}",
      path: {
        organization_id: organizationId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Update Organization
   * @param organizationId
   * @param requestBody
   * @returns Organization Successful Response
   * @throws ApiError
   */
  public static updateOrganizationOrganizationsOrganizationIdPut(
    organizationId: string,
    requestBody: OrganizationUpdate
  ): CancelablePromise<Organization> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/organizations/{organization_id}",
      path: {
        organization_id: organizationId,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Delete Organization
   * @param organizationId
   * @returns any Successful Response
   * @throws ApiError
   */
  public static deleteOrganizationOrganizationsOrganizationIdDelete(
    organizationId: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/organizations/{organization_id}",
      path: {
        organization_id: organizationId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * List Organization Members
   * @param organizationUuid
   * @returns UserWithMembership Successful Response
   * @throws ApiError
   */
  public static listOrganizationMembersOrganizationsMembersGet(
    organizationUuid: string
  ): CancelablePromise<Array<UserWithMembership>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/organizations/members",
      query: {
        organization_uuid: organizationUuid,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Create Organization Member
   * @param requestBody
   * @returns UserWithMembership Successful Response
   * @throws ApiError
   */
  public static createOrganizationMemberOrganizationsMembersPost(
    requestBody: OrganizationMemberCreate
  ): CancelablePromise<UserWithMembership> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/organizations/members",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Remove User
   * @param requestBody
   * @returns any Successful Response
   * @throws ApiError
   */
  public static removeUserOrganizationsMembersPatch(
    requestBody: OrganizationMemberDelete
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/organizations/members",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Update Organization Membership
   * @param requestBody
   * @returns any Successful Response
   * @throws ApiError
   */
  public static updateOrganizationMembershipOrganizationsMemberPut(
    requestBody: OrganizationMemberUpdate
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/organizations/member",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
