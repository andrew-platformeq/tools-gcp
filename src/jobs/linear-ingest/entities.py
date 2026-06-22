"""Linear GraphQL entity definitions for bronze extraction."""

from __future__ import annotations

from dataclasses import dataclass

PAGE_SIZE = 250
OVERLAP_MINUTES = 5
WATERMARKS_VERSION = 1
EPOCH = "1970-01-01T00:00:00.000Z"


@dataclass(frozen=True)
class EntityConfig:
    name: str
    connection: str
    node_fields: str
    incremental: bool = True
    paginated: bool = True


ENTITIES: list[EntityConfig] = [
    EntityConfig(
        name="organization",
        connection="organization",
        node_fields="""
            id name urlKey userCount createdAt updatedAt
        """,
        incremental=False,
        paginated=False,
    ),
    EntityConfig(
        name="teams",
        connection="teams",
        node_fields="""
            id key name description icon color createdAt updatedAt archivedAt
            cyclesEnabled timezone
        """,
        incremental=False,
    ),
    EntityConfig(
        name="workflow_states",
        connection="workflowStates",
        node_fields="""
            id name type position createdAt updatedAt archivedAt
            team { id }
        """,
        incremental=False,
    ),
    EntityConfig(
        name="issue_labels",
        connection="issueLabels",
        node_fields="""
            id name description color isGroup createdAt updatedAt archivedAt
            retiredAt lastAppliedAt
            team { id }
            parent { id }
        """,
        incremental=False,
    ),
    EntityConfig(
        name="users",
        connection="users",
        node_fields="""
            id name displayName email avatarUrl title timezone
            active admin owner guest app isMe isAssignable
            createdAt updatedAt archivedAt lastSeen
        """,
    ),
    EntityConfig(
        name="projects",
        connection="projects",
        node_fields="""
            id name description slugId icon color
            state startDate targetDate startedAt completedAt canceledAt
            progress health priority sortOrder
            createdAt updatedAt archivedAt trashed
            lead { id }
            creator { id }
        """,
    ),
    EntityConfig(
        name="cycles",
        connection="cycles",
        node_fields="""
            id number name description
            startsAt endsAt completedAt
            isActive isFuture isPast isNext isPrevious
            progress currentProgress
            createdAt updatedAt archivedAt
            team { id }
        """,
    ),
    EntityConfig(
        name="issues",
        connection="issues",
        node_fields="""
            id identifier number title description url branchName
            priority estimate sortOrder labelIds
            trashed snoozedUntilAt dueDate
            createdAt updatedAt archivedAt
            startedAt completedAt canceledAt
            addedToProjectAt addedToCycleAt addedToTeamAt
            team { id }
            state { id }
            assignee { id }
            creator { id }
            delegate { id }
            project { id }
            cycle { id }
            parent { id }
            projectMilestone { id }
        """,
    ),
    EntityConfig(
        name="comments",
        connection="comments",
        node_fields="""
            id body bodyData issueId projectId
            parentId resolvingCommentId
            createdAt updatedAt archivedAt editedAt resolvedAt
            url isArtificialAgentSessionRoot
            user { id }
            issue { id }
        """,
    ),
    EntityConfig(
        name="attachments",
        connection="attachments",
        node_fields="""
            id title subtitle url metadata source sourceType
            createdAt updatedAt archivedAt
            issue { id }
            creator { id }
        """,
    ),
]
