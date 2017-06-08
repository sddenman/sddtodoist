from todoist import TodoistAPI
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


def add_item(title: str, project_id: int, due_date: str = "today", priority: int = 4, comment: str = "",
             attachment: object = None, labels: list = None
             ) -> _todoistmodels.Item:

    label_ids = []
    if labels:
        for label_name in labels:
            label_ids.append(_todoistapi.labels.add(label_name)['id'])

    new_item = _todoistapi.items.add(content=title,
                                     date_string=due_date,
                                     priority=priority,
                                     project_id=project_id,
                                     labels=label_ids
                                     )

    if attachment:
        add_comment(comment, new_item['id'], attachment)
    elif comment:
        add_comment(comment, new_item['id'])
    else:
        pass

    _todoistapi.commit()

    return new_item


def add_comment(text: str, item_id: int, attachment: object = None) -> _todoistmodels.Note:

    if attachment:
        new_note = _todoistapi.notes.add(item_id, content=text, file_attachment=attachment)
    else:
        new_note = _todoistapi.notes.add(item_id, content=text)

    _todoistapi.commit()

    return new_note


def add_label(name: str, item_id: int = None) -> _todoistmodels.Label:

    new_label = _todoistapi.labels.add(name)

    if item_id:
        item = _todoistapi.items.get_by_id(item_id)
        item.update(labels=item['labels'].append(new_label['id']))

    _todoistapi.commit()

    return new_label


def add_project(name: str, parent_project_id: int = None) -> _todoistmodels.Project:

    if parent_project_id is not None:
        parent_project_obj = _todoistapi.projects.get_by_id(parent_project_id)
        new_project = _todoistapi.projects.add(
            name,
            item_order=parent_project_obj['item_order'],
            indent=parent_project_obj['indent']+1
        )
    else:
        new_project = _todoistapi.projects.add(name)

    _todoistapi.commit()

    return new_project


def remove_project(project_id: int, delete_project: bool = False) -> _todoistmodels.Project:

    if delete_project:
        removed_project = _todoistapi.projects.delete(project_id)
    else:
        removed_project = _todoistapi.projects.archive(project_id)

    _todoistapi.commit()

    return removed_project


def get_project_by_name(name: str) -> list:

    projects = []
    for project in get_sync_response()['projects']:
        if project['name'] == name:
            projects.append(project)

    return projects


def get_sync_response() -> _todoistmodels.Model:

    _todoistapi.reset_state()
    sync_response = _todoistapi.sync()

    return sync_response


def write_result_and_exit(exit_code: int,
                          vars_args: object,
                          return_obj: _todoistmodels.Model = None,
                          cmdline_msg: str = None
                          ):

    if vars_args['pipeobj']:
        if return_obj:
            sys.stdout.write(str(return_obj))
    elif vars_args['pipeid']:
        if return_obj:
            return_obj_ids = []
            try:
                return_obj_ids.append(return_obj['id'])
            except:
                for sub_obj in return_obj:
                    try:
                        return_obj_ids.append(sub_obj['id'])
                    except:
                        pass
            sys.stdout.write(str(return_obj_ids))
    else:
        if cmdline_msg:
            print(cmdline_msg)

    sys.exit(exit_code)


def pformat_todoist_obj(todoist_obj: _todoistmodels.Model) -> str:

    return _todoistmodels.pformat(todoist_obj, indent=4)


def upload_file(filename) -> _todoistmodels.Model:

    return _todoistapi.uploads.add(filename)


_apitoken = ConfigVal('apitoken').value
_todoistapi = TodoistAPI(_apitoken)
