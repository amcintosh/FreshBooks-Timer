import logging

from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.model.project import Project
from fbtimer.service.auth import auth


log = logging.getLogger(__name__)


def get_project(user, project_id):
    res = auth(user.token, include_content_type=False).get(
        '{}projects/business/{}/project/{}'
        .format(FRESHBOOKS_BASE_URL, user.business_id, project_id)
    ).json()
    log.debug('Project response: %s', res)

    if res.get('project'):
        return Project(res.get('project'))
    return None


def get_projects(user):
    res = auth(user.token, include_content_type=False).get(
        '{}projects/business/{}/projects?active=1&page=0'
        .format(FRESHBOOKS_BASE_URL, user.business_id)
    ).json()
    log.debug('Projects response: %s', res)

    projects = res.get('projects', [])
    if len(projects) == 0:
        return projects
    return [Project(a) for a in projects]


def get_client_projects(user, client_id):
    projects = get_projects(user)
    filtered_projects = []

    for project in projects:
        if client_id == project.client_id:
            filtered_projects.append(project)

    return filtered_projects
