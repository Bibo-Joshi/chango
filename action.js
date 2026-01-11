/*
* SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
*
* SPDX-License-Identifier: MIT
*/
module.exports = async ({github, context, core, query_issue_types}) => {
    const pullRequest = context.payload.pull_request;
    if (!pullRequest) {
        // This action only runs on pull_request events. Skip with debug message but
        // do not fail the action.
        console.log('No pull request found in the context. Not fetching additional data.');
        return;
    }

    const use_query_issue_types = query_issue_types === 'true';

    // Fetch the linked issues
    const data = await github.graphql(`
        query {
            repository(owner:"${context.repo.owner}", name:"${context.repo.repo}") {
                pullRequest(number:${context.payload.pull_request.number}) {
                    closingIssuesReferences(first: 100) {
                        nodes {
                            number
                            title
                            ${use_query_issue_types ? 'issueType { name }' : ''}
                            labels(first: 100) {
                                nodes {
                                    name
                                    id
                                }
                            }
                        }
                    }
                }
            }
        }
    `, {
        headers: {
            "GraphQL-Features": "issue_types"
        }
    });

    const closingIssues = data.repository.pullRequest.closingIssuesReferences.nodes.map(node => {
        return {
            number: node.number,
            title: node.title,
            labels: node.labels.nodes.map(label => label.name),
            issueType: node.issueType ? node.issueType.name : null
        };
    });

    // Fetch the parent PR
    const response = await github.graphql(`
        query {
            search(
                type: ISSUE,
                query: "org:${context.repo.owner} repo:${context.repo.repo} is:pr head:${context.payload.pull_request.base.ref}"
                first: 100
            ) {
                issueCount
                nodes {
                    ... on PullRequest {
                        number
                        title
                        url
                        state
                        author {
                            login
                        }
                        baseRepository {
                            owner {
                                login
                            }
                        }
                        headRepository {
                            owner {
                                login
                            }
                        }
                    }
                }
            }
        }
    `);
    const prs = response.search.nodes;
    let parentPR = prs.length > 0 ? prs[0] : null;
    if (parentPR) {
        parentPR.author_login = parentPR.author.login;
        delete parentPR.author;
    }

    if (parentPR && parentPR.baseRepository?.owner?.login === parentPR.headRepository?.owner?.login) {
        // The parent PR is from the same owner as the base repo, so it is not a fork
        delete parentPR.baseRepository;
        delete parentPR.headRepository;
    } else {
        // Parent PR is from a fork, discard it
        parentPR = null;
    }

    // Combine the linked issues and the parent PR to a single JSON object
    const linkedIssuesAndParentPR = {
        linked_issues: closingIssues,
        parent_pull_request: parentPR
    };
    core.setOutput('data', JSON.stringify(linkedIssuesAndParentPR));
};