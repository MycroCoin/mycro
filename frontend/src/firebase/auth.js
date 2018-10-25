import { auth } from './firebase';

export const getAuth = () => {
  return auth();
};

export const githubOAuth = () => {
  return new auth.GithubAuthProvider();
};
