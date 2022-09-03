Assigning organizations to users
--------------------------------

### Current state

- **Joining an org.** I assign you by hand to organizations. It’s an insert on an existing account.
- **User onboarding.** You onboard by signing up through and receiving a token from Auth0,
  then calling our system with that token (this happens automatically, all requests from the frontend use this token, which saves to local storage).
  Our system checks that the token is authentic, and if it is, it then looks if we already have your user in our database. If it doesn’t, we add it.
- **Source of truth for organizations.** The ``organization_members`` table is where we canonically define who belongs to which org.
- **Source of truth for users.** Technically auth0. There’s some world where you could sign up with us and not call any of our APIs, so we’d never know you existed. I’m sure we could remedy this, I just don’t understand auth0 well enough to know how.

### Desired state

- **Joining an org.** You sign up, and create an organization if yours does not already exist. Organization is determined by email domain, and you can add external parties via an email invite.
- **User onboarding.** You sign up via Auth0 and instantly we know your account exists in our ``users`` table. It should not be possible for Auth0 and our own work to get out of sync.
