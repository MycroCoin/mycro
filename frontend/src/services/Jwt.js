const JWT_KEY = 'jwt';

const setJwt = newJwt => {
  localStorage.setItem(JWT_KEY, newJwt);
};

const clearJwt = () => {
  localStorage.removeItem(JWT_KEY);
};

const getJwt = () => {
  return localStorage.getItem(JWT_KEY);
};

export { setJwt, getJwt, clearJwt };
