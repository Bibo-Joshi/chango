/*
* SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
*
* SPDX-License-Identifier: MIT
*/
module.exports = async function (github, context, core, inputs) {
// if issue types are requested but no organization scoped PAT is provided, fail the action
    if ((inputs.query - issue - types) && !inputs.github - token))
    {
        core.setFailed('Cannot query issue types without an organization scoped PAT.');
        return;
    }

    const pullRequest = context.payload.pull_request;
    if (!pullRequest) {
        // This action only runs on pull_request events. Skip with debug message but
        // do not fail the action.
        console.log('No pull request found in the context. Not fetching additional data.');
        return;
    }

    // Fetch the linked issues
    const data = await github.graphql(`
        query {
            repository(owner:"${context.repo.owner}", name:"${context.repo.repo}") {
                pullRequest(number:${context.payload.pull_request.number}) {
                    closingIssuesReferences(first: 100) {
                        nodes {
                            number
                            title
                            ${inputs.query-issue-types ? 'issueType { name }' : ''}
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
    `);

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
                query: "org:${context.repo.owner} repo:${context.repo.repo} is:pr base:main head:${context.payload.pull_request.base.ref}"
                first: 100
            ) {
                issueCount
                nodes {
                    ... on PullRequest {
                        number
                        title
                        url
                        state
                    }
                }
            }
        }
    `);
    const prs = response.search.nodes;
    const parentPR = prs.length > 0 ? prs[0] : null;

    // Combine the linked issues and the parent PR to a single JSON object
    const linkedIssuesAndParentPR = {
        linked_issues: closingIssues,
        parent_pull_request: parentPR
    };
    // debug-print the context
    console.log(JSON.stringify(linkedIssuesAndParentPR, null, 2));
    core.setOutput('data', JSON.stringify(linkedIssuesAndParentPR));
}