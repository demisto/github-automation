import os
import sys

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()


class GraphQLClient(object):
    BASE_URL = 'https://api.github.com'

    def __init__(self, api_key=None):
        api_key = api_key if api_key else os.getenv("GITHUB_TOKEN")  # TODO: add explanation in readme
        sample_transport = RequestsHTTPTransport(
            url=self.BASE_URL + '/graphql',
            use_json=True,
            headers={
                'Authorization': f"Bearer {api_key}"
            },
            verify=False
        )
        self.client = Client(
            transport=sample_transport,
            fetch_schema_from_transport=True,
        )

    def execute_query(self, query, variable_values=None):
        gql_query = gql(query)
        try:
            response = self.client.execute(gql_query, variable_values=variable_values)
            return response
        except Exception as ex:
            if 'API rate limit exceeded' in str(ex):
                print("API rate limit exceeded")
                sys.exit(0)

            raise

    def get_github_issues(self, owner, name, after, labels, milestone):
        vars = {"owner": owner, "name": name, "labels": labels, "milestone": milestone, "after": after}
        if not milestone:
            del vars['milestone']
        if not after:
            del vars['after']
        if not labels:
            del vars['labels']
            return self.execute_query('''
                    query ($after: String, $owner: String!, $name: String!, $milestone: String){
                      repository(owner: $owner, name: $name) {
                        issues(first: 100, after:$after, states: OPEN, filterBy:{milestone: $milestone}) {
                          pageInfo {
                            hasNextPage
                            endCursor
                          }
                          edges {
                            cursor
                            node {
                            projectCards(first:5){
                            nodes{
                              id
                              column {
                                name
                              }
                              project{
                                number
                                }
                              }
                            }
                              timelineItems(first:10, itemTypes:[CROSS_REFERENCED_EVENT]){
                                __typename
                                ... on IssueTimelineItemsConnection{
                                  nodes {
                                    ... on CrossReferencedEvent {
                                      willCloseTarget
                                      source {
                                        __typename
                                        ... on PullRequest {
                                          id
                                          title
                                          state
                                          isDraft
                                          assignees(first:10){
                                            nodes{
                                              login
                                            }
                                          }
                                          labels(first:5){
                                            nodes{
                                              name
                                            }
                                          }
                                          reviewRequests(first:1){
                                            totalCount
                                          }
                                          reviews(first:1){
                                            totalCount
                                          }
                                          number
                                          reviewDecision
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                              title
                              id
                              number
                              state
                              milestone {
                                title
                              }
                              labels(first: 10) {
                                edges {
                                  node {
                                    name
                                  }
                                }
                              }
                              assignees(last: 10) {
                                edges {
                                  node {
                                    id
                                    login
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }''', vars)
        return self.execute_query('''
        query ($after: String, $owner: String!, $name: String!, $labels: [String!], $milestone: String){
          repository(owner: $owner, name: $name) {
            issues(first: 100, after:$after, states: OPEN, filterBy:{labels: $labels, milestone: $milestone}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              edges {
                cursor
                node {
                    projectCards(first:5){
                    nodes{
                      id
                      column {
                        name
                      }
                      project{
                        number
                      }
                    }
                  }
                  timelineItems(first:10, itemTypes:[CROSS_REFERENCED_EVENT]){
                    __typename
                    ... on IssueTimelineItemsConnection{
                      nodes {
                        ... on CrossReferencedEvent {
                          willCloseTarget
                          source {
                            __typename
                            ... on PullRequest {
                              id
                              title
                              state
                              isDraft
                              assignees(first:10){
                                nodes{
                                  login
                                }
                              }
                              labels(first:5){
                                nodes{
                                  name
                                }
                              }
                              reviewRequests(first:1){
                                totalCount
                              }
                              reviews(first:1){
                                totalCount
                              }
                              number
                              reviewDecision
                            }
                          }
                        }
                      }
                    }
                  }
                  title
                  id
                  number
                  milestone {
                    title
                  }
                  labels(first: 10) {
                    edges {
                      node {
                        name
                      }
                    }
                  }
                  assignees(last: 10) {
                    edges {
                      node {
                        id
                        login
                      }
                    }
                  }
                }
              }
            }
          }
        }''', vars)

    def get_github_pull_requests(self, owner, name, after):
        vars = {"owner": owner, "name": name, "after": after}
        if not after:
            del vars['after']
        return self.execute_query('''
                query ($after: String, $owner: String!, $name: String!) {
                  repository(owner: $owner, name: $name) {
                    pullRequests(first: 100, after:$after, states: OPEN) {
                      pageInfo {
                        endCursor
                        hasNextPage
                      }
                      edges {
                        cursor
                        node {
                          title
                          id
                          state
                          number
                          mergedAt
                          merged
                          reviewDecision
                          reviews(last: 10) {
                            totalCount
                          }
                          reviewRequests(first: 10) {
                            totalCount
                          }
                          labels(first: 10) {
                            edges {
                              node {
                                name
                              }
                            }
                          }
                          assignees(last: 10) {
                            edges {
                              node {
                                id
                                login
                              }
                            }
                          }
                          projectCards(first: 5) {
                            nodes {
                              id
                              column {
                                name
                              }
                              project {
                                number
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
                ''', vars)

    def add_items_to_project(self, issue_id, column_id):
        return self.execute_query('''
        mutation addProjectCardAction($contentID: ID!, $columnId: ID!){
          addProjectCard(input: {contentId: $contentID, projectColumnId: $columnId}) {
            cardEdge{
              node{
                id
              }
            }
          }
        }''', {'contentID': issue_id, 'columnId': column_id})

    def add_to_column(self, card_id, column_id):
        variable_dict = {'cardId': card_id, 'columnId': column_id}

        self.execute_query('''
        mutation moveProjectCardAction($cardId: ID!, $columnId: ID!){
          moveProjectCard(input: {cardId: $cardId, columnId: $columnId}) {
            cardEdge{
              node{
                id
              }
            }
          }
        }''', variable_dict)

    def move_to_specific_place_in_column(self, card_id, column_id, after_card_id):
        variable_dict = {'cardId': card_id, 'columnId': column_id, 'afterCardId': after_card_id}

        self.execute_query('''
        mutation moveProjectCardAction($cardId: ID!, $columnId: ID!, $afterCardId: ID!){
          moveProjectCard(input: {cardId: $cardId, columnId: $columnId, afterCardId: $afterCardId}) {
            cardEdge{
              node{
                id
              }
            }
          }
        }''', variable_dict)

    def delete_project_card(self, card_id):
        return self.execute_query('''
        mutation deleteProjectCardAction($cardId: ID!){
          deleteProjectCard(input: {cardId: $cardId}) {
            deletedCardId
          }
        }''', {'cardId': card_id})

    def get_project_layout(self, owner, repository_name, project_number, is_org_project=False):
        query_args = {"owner": owner, "name": repository_name, "number": project_number}
        query = '''
        project(number: $number) {
          name
          id
          number
          columns(first: 15) {
            edges{
              cursor
              node {
                name
              }
            }
          }
        }
      }
    }'''
        if is_org_project:
            # replace repository query with org query and remove name for args
            query_prefix = '''query ($owner: String!, $number: Int!) {
            organization(login: $owner) {\n'''
            del query_args['name']
        else:
            query_prefix = '''query ($owner: String!, $name: String!, $number: Int!){
            repository(owner: $owner, name: $name) {\n'''
        query = query_prefix + query
        return self.execute_query(query, query_args)

    def get_issue(self, owner, name, issue_number):
        return self.execute_query('''
        query ($owner: String!, $name: String!, $issueNumber: Int!){
  repository(owner: $owner, name: $name) {
    issue(number: $issueNumber) {
      projectCards(first:5){
        nodes{
          id
          column {
            name
          }
          project{
            number
          }
        }
      }
      timelineItems(first: 5, itemTypes: [CROSS_REFERENCED_EVENT]) {
        __typename
        ... on IssueTimelineItemsConnection {
          nodes {
            ... on CrossReferencedEvent {
              willCloseTarget
              source {
                __typename
                ... on PullRequest {
                  id
                  title
                  state
                  isDraft
                  assignees(first: 5) {
                    nodes {
                      login
                    }
                  }
                  labels(first:5){
                    nodes{
                      name
                    }
                  }
                  reviewRequests(first:1){
                    totalCount
                  }
                  reviews(first:1){
                    totalCount
                  }
                  number
                  reviewDecision
                }
              }
            }
          }
        }
      }
      title
      id
      number
      state
      milestone {
        title
      }
      labels(last: 10) {
        edges {
          node {
            name
          }
        }
      }
      assignees(last: 10) {
        edges {
          node {
            id
            login
          }
        }
      }
    }
  }
}
''', {"owner": owner, "name": name, "issueNumber": issue_number})

    def get_pull_request(self, owner, name, pull_request_number):
        return self.execute_query('''
query ($owner: String!, $name: String!, $prNumber: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $prNumber) {
      projectCards(first: 5) {
        nodes {
          id
          column {
            name
          }
          project {
            number
          }
        }
      }
      title
      id
      number
      state
      mergedAt
      merged
      reviewDecision
      reviews(last: 10) {
        totalCount
      }
      reviewRequests(first: 10) {
        totalCount
      }
      labels(last: 10) {
        edges {
          node {
            name
          }
        }
      }
      assignees(last: 10) {
        edges {
          node {
            id
            login
          }
        }
      }
    }
  }
}
''', {"owner": owner, "name": name, "prNumber": pull_request_number})

    def get_column_items(self, owner, name, project_number, prev_column_id, start_cards_cursor='',
                         is_org_project=False):
        query_args = {"owner": owner, "name": name, "projectNumber": project_number, "prevColumnID": prev_column_id,
                      "start_cards_cursor": start_cards_cursor}
        query = '''
    project(number: $projectNumber) {
      name
      id
      number
      columns(after: $prevColumnID, first: 1) {
        nodes {
          name
          id
          cards(first: 100, after: $start_cards_cursor) {
            pageInfo {
              endCursor
              hasNextPage
            }
            edges {
              cursor
              node {
                note
                state
                id
                content {
                  __typename
                  ... on Issue {
                    id
                    number
                    title
                    labels(first: 10) {
                      edges {
                        node {
                          name
                        }
                      }
                    }
                    assignees(first: 10) {
                      edges {
                        node {
                          login
                        }
                      }
                    }
                  }
                  ... on PullRequest {
                    id
                    number
                    title
                    labels(first: 10) {
                      edges {
                        node {
                          name
                        }
                      }
                    }
                    reviewDecision
                    reviews(last: 10) {
                      totalCount
                    }
                    reviewRequests(first: 10) {
                      totalCount
                    }
                    assignees(first: 10) {
                      edges {
                        node {
                          login
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
'''
        if is_org_project:
            # replace repository query with org query and remove name for args
            query_prefix = '''query ($owner: String!, $projectNumber: Int!, $prevColumnID: String!, $start_cards_cursor: String) {
            organization(login: $owner) {\n'''
            del query_args['name']
        else:
            query_prefix = '''query ($owner: String!, $name: String!, $projectNumber: Int!, $prevColumnID: String!, $start_cards_cursor: String) {
            repository(owner: $owner, name: $name) {\n'''
        query = query_prefix + query
        return self.execute_query(query, query_args)

    def get_first_column_items(self, owner, name, project_number, start_cards_cursor='', is_org_project=False):
        query_args = {"owner": owner, "name": name, "projectNumber": project_number,
                      "start_cards_cursor": start_cards_cursor}
        query = '''
        project(number: $projectNumber) {
          name
          id
          number
          columns(first: 1) {
            nodes {
              name
              id
              cards(first: 100, after: $start_cards_cursor) {
                pageInfo {
                  endCursor
                  hasNextPage
                }
                edges {
                  cursor
                  node {
                    note
                    state
                    id
                    content {
                      __typename
                      ... on Issue {
                        id
                        number
                        title
                        labels(first: 10) {
                          edges {
                            node {
                              name
                            }
                          }
                        }
                        assignees(first: 10) {
                          edges {
                            node {
                              login
                            }
                          }
                        }
                      }
                      ... on PullRequest {
                        title
                        id
                        state
                        number
                        mergedAt
                        merged
                        reviewDecision
                        reviews(last: 10) {
                          totalCount
                        }
                        reviewRequests(first: 10) {
                          totalCount
                        }
                        labels(first: 10) {
                          edges {
                            node {
                              name
                            }
                          }
                        }
                        assignees(first: 10) {
                          edges {
                            node {
                              login
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    '''
        if is_org_project:
            # replace repository query with org query and remove name for args
            query_prefix = '''query ($owner: String!, $projectNumber: Int!, $start_cards_cursor: String) {
            organization(login: $owner) {\n'''
            del query_args['name']
        else:
            query_prefix = '''query ($owner: String!, $name: String!, $projectNumber: Int!, $start_cards_cursor: String) {
            repository(owner: $owner, name: $name) {\n'''
        query = query_prefix + query
        return self.execute_query(query, query_args)

    def un_archive_card(self, card_id):
        return self.execute_query(''' mutation ($card_id: ID!, $isArchived: Boolean){
        updateProjectCard(input: {projectCardId: $card_id, isArchived: $isArchived}) {
          projectCard {
            isArchived
          }
        }
      }''', {'card_id': card_id, "isArchived": False})
