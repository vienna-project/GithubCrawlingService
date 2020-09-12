"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com

Github GraphQL Query 문들을 저장
"""

# API URL
GITHUB_URL = "https://api.github.com"
GITHUB_REPOSITORY_ID_URL = "https://api.github.com/repositories/"
GITHUB_GQL = "https://api.github.com/graphql"


# API Rate Limit 을 가져오기 위한 graphQL Query
GETLIMIT_QUERY = '''
query {
  rateLimit(dryRun:true) {
    limit,
    cost,
    remaining,
    resetAt
  }  
}
'''

# Github Repostiory의 Metadata을 가져오기 위한 graphQL Query
GETREPO_QUERY = """
query GetRepo($owner: String!, $name: String!) { 
  repository(owner:$owner, name:$name) {
    id, 
    name,
	  owner {
      login
    },
    homepageUrl,
    openGraphImageUrl,
    createdAt,
    updatedAt,  
    pushedAt,
    description,
    diskUsage,
    forkCount,
    hasWikiEnabled,
    hasIssuesEnabled,
    hasProjectsEnabled,
    isFork,    
    isArchived,
    isDisabled,
    isEmpty,
    isFork,
    isLocked,
    isMirror,
    isPrivate,
    isTemplate,
    mergeCommitAllowed,

    watchers(first:1){
      totalCount
    },

    stargazers(first:1){
      totalCount
    },

    commitComments(first:1){
      totalCount
    },

    pullRequests {
      totalCount
    },

    releases(first:1) {
      totalCount
    },

    primaryLanguage {
      name
    },

    languages(first:100) {
      nodes {
        name
      }
    },

    labels(first:1) {
      totalCount
    },

    licenseInfo {
      name
    },

    deployments {
      totalCount
    },

    repositoryTopics(first:100){
      nodes {
        topic{
          name
        }
      }
    },    
  },
  
  rateLimit {
    limit,
    cost,
    remaining,
    resetAt
  }  
}
"""
