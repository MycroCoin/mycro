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
        isMycroDao,
        url,
        ascs{
          hasExecuted
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
      url, 
      threshold,
      totalSupply,
      ascs{
        id,
        reward,
        prId,
        address,
        voters,
        hasExecuted,
        voteAmount,
      },
      balances {
        address,
        balance
      },
      pullRequests {
        number,
        title,
        state
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
