import todoist
from todoist import models as _todoistmodels
import configparser
import os
import sys


class ConfigVal:

    def __init__(self, key: str, section: str = 'DEFAULT'):
        _configfile_pn = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.splitext(__file__)[0] + '.ini'
        )
        config = configparser.ConfigParser()
        config.read(_configfile_pn)
        self.section = section
        self.key = key
        self.value = config[section][key]


def add_item(title: str, project_id: int) -> _todoistmodels.Item:

    try:
        project = _todoistapi.projects.get_by_id(project_id)
    except AttributeError:
        raise

    new_item = _todoistapi.items.add(content=title, project_id=project)

    try:
        _todoistapi.commit()
    except todoist.api.SyncError:
        raise

    return new_item


def set_item_duedate(item_id: int, date_string: str) -> _todoistmodels.Item:

    try:
        item = _todoistapi.items.get_by_id(item_id)
    except AttributeError:
        raise

    item.update(date_string=date_string)

    try:
        _todoistapi.commit()
    except todoist.api.SyncError:
        raise

    return item


def set_item_priority(item_id: int, priority: int) -> _todoistmodels.Item:

    try:
        item = _todoistapi.items.get_by_id(item_id)
    except AttributeError:
        raise

    item.update(priority=priority)

    try:
        _todoistapi.commit()
    except todoist.api.SyncError:
        raise

    return item


def add_comment(text: str, item_id: int, attachment: object = None) -> _todoistmodels.Note:

    if attachment:
        new_note = _todoistapi.notes.add(item_id, content=text, file_attachment=attachment)
    else:
        new_note = _todoistapi.notes.add(item_id, content=text)

    try:
        _todoistapi.commit()
    except todoist.api.SyncError:
        raise

    return new_note


def add_label(name: str, item_id: int = None) -> _todoistmodels.Label:

    new_label = _todoistapi.labels.add(name)

    try:
        _todoistapi.commit()
    except todoist.api.SyncError:
        raise

    if item_id:
        try:
            item = _todoistapi.items.get_by_id(item_id)
        except AttributeError:
            raise
        new_item_labels = item['labels']
        new_item_labels[len(new_item_labels):] = [new_label['id']]
        item.update(labels=new_item_labels)
        try:
            _todoistapi.commit()
        except todoist.api.SyncError:
            raise

    return new_label


def add_project(name: str, parent_project_id: int = None) -> _todoistmodels.Project:

    if parent_project_id:
        try:
            parent_project_obj = _todoistapi.projects.get_by_id(parent_project_id)
        except AttributeError:
            raise
        new_project = _todoistapi.projects.add(name,
                                               item_order=parent_project_obj['item_order'],
                                               indent=parent_project_obj['indent']+1
                                               )
    else:
        new_project = _todoistapi.projects.add(name)

    try:
        _todoistapi.commit()
    except todoist.api.SyncError:
        raise

    return new_project


def remove_project(project_id: int, delete_project: bool = False) -> _todoistmodels.Project:

    try:
        _todoistapi.projects.get_by_id(project_id)
    except AttributeError:
        raise

    removed_project = _todoistapi.projects.delete([project_id]) if delete_project \
        else _todoistapi.projects.archive(project_id)

    try:
        _todoistapi.commit()
    except todoist.api.SyncError:
        raise

    return removed_project


def get_project_id_by_name(name: str) -> list:

    projects = []
    for project in get_sync_response()['projects']:
        if project['name'] == name:
            projects.append(project['id'])

    return projects


def get_inbox_project() -> _todoistmodels.Project:

    for project in get_sync_response()['projects']:
        if project['inbox_project']:
            return project


def get_email_by_id(object_id: int, object_type: str) -> str:

    email_obj = _todoistapi.emails.get_or_create(obj_id=object_id, obj_type=object_type)
    email = email_obj['email']
    return email


def get_sync_response() -> _todoistmodels.Model:

    _todoistapi.reset_state()

    try:
        return _todoistapi.sync()
    except todoist.api.SyncError:
        raise


def write_result_and_exit(exit_code: int,
                          vars_args: vars,
                          return_obj: object = None,
                          cmdline_msg: str = None
                          ):

    if vars_args['out']:
        if return_obj:
            if vars_args['out'] == "FULL":
                sys.stdout.write(str(return_obj))
            else:
                sys.stdout.write(str(find_key_in_object(return_obj, vars_args['out'])))
    else:
        if cmdline_msg:
            print(cmdline_msg)

    sys.exit(exit_code)


def find_key_in_object(obj: dict, key: str) -> list:
    try:
        return obj[key]
    except (KeyError, TypeError):
        try:
            return_list = []
            for i in obj:
                returnobj = find_key_in_object(i, key)
                if returnobj:
                    return_list.append(returnobj)
            return return_list
        except TypeError:
            return obj


def pformat_todoist_obj(todoist_obj: _todoistmodels.Model) -> str:

    return _todoistmodels.pformat(todoist_obj, indent=4)


def upload_file(filename) -> _todoistmodels.Model:

    return _todoistapi.uploads.add(filename)


_apitoken = ConfigVal('apitoken').value
_todoistapi = todoist.TodoistAPI(_apitoken)
