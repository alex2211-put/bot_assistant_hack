import enum


class ProjectStates(enum.Enum):
    PROJECT_NAME = 'project_name'
    PROJECT_DESCRIPTION = 'project_description'
    PROJECT_RESPONSIBLE = 'project_responsible'
    PROJECT_MAIN_MESSAGE = 'project_main_message'
    PROJECT_RECIPIENTS = 'project_recipients'
    ADD_RESPONSIBLE = 'add_responsible'
    ADD_RECIPIENTS = 'add_recipients'
    REMOVE_RECIPIENTS = 'remove_recipients'
    REMOVE_RESPONSIBLE = 'remove_responsible'
    ADD_OWNERS = 'add_owners'
