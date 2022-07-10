import { User } from "@auth0/auth0-react";

type Nullable<T> = T | null | undefined;

const isAdmin = (user: Nullable<User>) => {
  if (typeof user === "undefined") {
    return false;
  }
  return user?.email_verified && user?.email?.endsWith("@mercator.tech");
};

export { isAdmin };
