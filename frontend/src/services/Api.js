import client from '../GraphqlClient.js';
import gql from 'graphql-tag';

//MUTATIONS
const createProject = (projectName, creatorAddress) => 
  client.mutate({mutation: gql`
    mutation {
      createProject(projectName: "${projectName}", creatorAddress: "${creatorAddress}") {
        projectAddress 
      }
    }`});
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

//VIEWS
const listProjectsQuery = () => {
  return gql`
    query{
        allProjects {
        id,
        repoName,
        daoAddress,
        symbol,
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
        prId
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
};
