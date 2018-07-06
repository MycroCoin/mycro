import { ApolloClient } from 'apollo-client';
import { HttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';
import gql from 'graphql-tag';

const client = new ApolloClient({
  // By default, this client will send queries to the
  //  `/graphql` endpoint on the same host
  // Pass the configuration option { uri: YOUR_GRAPHQL_API_URL } to the `HttpLink` to connect
  // to a different host
  link: new HttpLink({
    uri: "http://localhost:8001"
  }),
  cache: new InMemoryCache(),
});

window.client = client;
const query = gql`query{
  getMergeAscAbi
}`;
client.query({query})
  .then((data, error) => {
    window.asc = data;
    window.error = error;
});
export default client;
