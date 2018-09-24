import client from '../GraphqlClient.js';
import gql from 'graphql-tag';
import {toChecksumAddress} from 'web3-utils';

//MUTATIONS
const createProject = (projectName) => {
  const creatorAddress = toChecksumAddress(window.web3.eth.accounts[0]);

  return client.mutate({mutation: gql`
    mutation {
      createProject(projectName: "${projectName}", creatorAddress: "${creatorAddress}") {
        projectAddress 
      }
    }`});
}
const createAsc = (checksumDaoAddress, 
                                checksumRewardeeAddress, 
                                reward,
                                prId) => 
  client.mutate({mutation: gql`
    mutation {
      createMergeAsc(
        daoAddress: "${checksumDaoAddress}",
        rewardee: "${checksumRewardeeAddress}", 
        reward: ${reward}, 
        prId: ${prId}) {
          asc {
            address
          } 
        }
    }`});

const loginUser = (provider, accessToken) => {
  return client.mutate({mutation: gql`
    mutation {
      socialAuth(provider: "${provider}", accessToken: "${accessToken}") {
        social {
          uid
        }
        token
      }
    }`});
}

//VIEWS
const listProjectsQuery = () => {
  return gql`
    query{
        allProjects {
        id,
        repoName,
        daoAddress,
        symbol,
        ascs{
          id
        },
      }
    }
  `;
}

const getProjectQuery = (address) => {
  return gql`
  query {
    project(daoAddress:"${address}") {
      id,
      daoAddress,
      repoName,
      symbol,
      ascs{
        id,
        reward,
        prId,
        address,
      },
      balances {
        address
        balance
      }
    }
  }`
}

export default {
  createAsc,
  createProject,
  listProjectsQuery,
  getProjectQuery,
  loginUser,
};
