#!/usr/bin/env python3

import argparse
from sddtodoist import *


def command_additem(command_args):

    vars_args = vars(command_args)

    if 'project' in vars_args:
        projects = get_project_by_name(vars_args['project'])
    else:
        projects = get_project_by_name('Inbox')

    if len(projects) == 0:
        write_result_and_exit(1, vars_args, None,
                              parser.prog+"ERROR: Project with name "+vars_args['project']+" not found.")
    elif len(projects) > 1:
        write_result_and_exit(1, vars_args, None,
                              parser.prog+"ERROR: Multiple projects with name "+vars_args['project']+" found.")
    else:
        add_item_args = {'project_id': projects[0]['id'], 'title': vars_args['name']}
        for key in ['due_date', 'comment', 'labels', 'priority']:
            if key in vars_args:
                add_item_args[key] = vars_args[key]
        if 'file' in vars_args:
            if vars_args['file'] is not None:
                add_item_args['attachment'] = upload_file(vars_args['file'].name)

        new_item = add_item(**add_item_args)

        write_result_and_exit(0, vars_args, new_item, parser.prog+" New item created with ID="+str(new_item['id'])+".")


def command_addlabel(command_args):

    vars_args = vars(command_args)

    # TODO Update command_addlabel to allow list of itemid's
    if vars_args['itemid']:
        new_label = add_label(vars_args['name'], vars_args['itemid'])
    else:
        new_label = add_label(vars_args['name'])

    write_result_and_exit(0, vars_args, new_label,
                          parser.prog +
                          " Label (name:" + str(new_label['name']) +
                          ", id:" + str(new_label['itemid']) +
                          ") added to item (id:" + str(vars_args['itemid']) +
                          ")."
                          )


def command_addproject(command_args):

    vars_args = vars(command_args)

    add_project_args = dict(name=vars_args['name'])

    if vars_args['parent']:
        project_objs = get_project_by_name(vars_args['project'])
        if len(project_objs) == 0:
            write_result_and_exit(0, vars_args, ,
                                  parser.prog +
                                  " (name:" + str(new_label['name']) +
                                  ", id:" + str(new_label['itemid']) +
                                  ") added to item (id:" + str(vars_args['itemid']) +
                                  ")."
                                  )
            print(parser.prog, "ERROR: Parent project", command_args.project, "not found.")
            sys.exit(1)
        elif len(project_objs) > 1:
            print(parser.prog, "ERROR: Multiple parent projects named", command_args.project, "found.")
            sys.exit(1)
        else:
            add_project_args['parent_project_id'] = project_objs[0]['id']

    new_project = add_project(**add_project_args)

    if vars_args['pipeobj']:
        sys.stdout.write(str(vars(new_project['project'])))
    elif vars_args['pipeid']:
        sys.stdout.write(str(new_project['project']['id']))
    else:
        print(parser.prog, "New project created with ID=", str(new_project['project']['id']))

    sys.exit(0)


def command_removeproject(command_args):

    vars_args = vars(command_args)

    removed_project = remove_project(vars_args['id'], vars_args['delete'])

    if vars_args['delete']:
        action = "deleted"
    else:
        action = "archived"

    write_result_and_exit(0, vars_args, removed_project,
                          parser.prog + "Project with ID=" + str(removed_project['id']) +
                          " and Name=" + removed_project['name'] + " " + action + "."
                          )


def command_addcomment(command_args):

    vars_args = vars(command_args)

    if 'file' in vars_args and vars_args['file'] is not None:
        attachment_obj = upload_file(vars_args['file'].name)
    else:
        attachment_obj = None

    new_comment = add_comment(vars_args['text'], item_id=vars_args['itemid'], attachment=attachment_obj)

    if vars_args['pipeobj']:
        sys.stdout.write(str(new_comment))
    elif vars_args['pipeid']:
        sys.stdout.write(str(new_comment['id']))
    else:
        print(parser.prog, "New comment created for item ID ", vars_args['itemid'], " with ID=", str(new_comment['id']))

    sys.exit(0)


def command_getsyncresponse(command_args):

    vars_args = vars(command_args)

    sync_response = get_sync_response()

    if vars_args['key']:
        try:
            key_value = sync_response[vars_args['key']]
            write_result_and_exit(0,
                                  vars_args,
                                  key_value,
                                  vars_args['key'] + ": \n" +
                                  str(pformat_todoist_obj(key_value))
                                  )
        except:
            write_result_and_exit(1, vars_args, None, parser.prog + " ERROR: " + vars_args['key'] + " key not found.")
    else:
        write_result_and_exit(0,
                              vars_args,
                              sync_response,
                              str(pformat_todoist_obj(sync_response))
                              )


def command_notimplemented(command_args):

    print(parser.prog, "Command", command_args.command, "not yet implemented.")
    sys.exit(1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Access Todoist web api")
    pipe_options_group = parser.add_mutually_exclusive_group()
    pipe_options_group.add_argument("--pipeobj", action='store_true', help="write return object(s) to stdout")
    pipe_options_group.add_argument("--pipeid", action='store_true', help="write return object ID(s) to stdout")

    subparsers = parser.add_subparsers(description='Sub-command description', help='sub-command help', dest='command')

    parser_additem = subparsers.add_parser("additem", aliases=['ai'], help="create a new item")
    parser_additem.add_argument("name", type=str, help="item name")
    parser_additem.add_argument("-d", "--due_date", type=str, default="today", help="due date (Todoist date_string)")
    parser_additem.add_argument("-c", "--comment", type=str, help="add comment")
    parser_additem.add_argument("-l", "--labels", type=str, nargs="+", help="add label(s)")
    parser_additem.add_argument("-n", "--priority", type=int, default=1, help="set priority (1=highest, 4=lowest)")
    parser_additem.add_argument("-f", "--file", type=argparse.FileType('r'), help="file to upload/attach to comment")
    parser_additem.add_argument("-p", "--project", type=str, default="Inbox", help="parent project of item")
    parser_additem.set_defaults(func=command_additem)

    parser_addlabel = subparsers.add_parser("addlabel", aliases=['al'], help="create label, optionally add to item(s)")
    parser_addlabel.add_argument("name", type=str, help="label name (will be created if it doesn't exist)")
    parser_addlabel.add_argument("-i", "--itemids", type=int, help="Add label to this(these) item ID(s)")
    parser_addlabel.set_defaults(func=command_addlabel)

    parser_addcomment = subparsers.add_parser("addcomment", aliases=['ac'], help="add a comment to an item")
    parser_addcomment.add_argument("text", type=str, help="comment text")
    parser_addcomment.add_argument("-f", "--file", type=argparse.FileType('r'), help="file to upload/attach to comment")
    parser_addcomment.add_argument("-i", "--itemid", type=int, required=True, help="Add comment to this item ID")
    parser_addcomment.set_defaults(func=command_addcomment)

    parser_addproject = subparsers.add_parser("addproject", aliases=['ap'], help="create a new project")
    parser_addproject.add_argument("name", type=str, help="project name")
    parser_addproject.add_argument("-p", "--parent", type=str, help="parent project of project")
    parser_addproject.set_defaults(func=command_addproject)

    parser_removeproject = subparsers.add_parser("removeproject", aliases=['rp'], help="remove project by archiving")
    parser_removeproject.add_argument("id", type=int, help="project id")
    parser_removeproject.add_argument("-d", "--delete", action='store_true', help="delete instead of archive")
    parser_removeproject.set_defaults(func=command_removeproject)

    parser_getsyncresponse = subparsers.add_parser("getsyncresponse", aliases=['gsr'], help="get todoist data")
    parser_getsyncresponse.add_argument("-k", "--key", type=str, help="key name (e.g., items, projects)")
    parser_getsyncresponse.set_defaults(func=command_getsyncresponse)

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_usage()
