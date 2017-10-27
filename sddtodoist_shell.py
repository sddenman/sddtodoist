#!/usr/bin/env python3

from sddtodoist import *
import todoist
import argparse
import fileinput
import sys


def command_additem(args):

    if args['id']:
        project_id = args['id']
    else:
        project_id = get_inbox_project()['id']

    try:
        item = add_item(title=args['name'], project_id=project_id)
        write_result_and_exit(0, args, item,
                              par.prog + ": New item with ID=" + str(item['id']) +
                              " created in project with ID=" + str(project_id) + ".")
    except AttributeError:
        write_result_and_exit(1, args, None,
                              par.prog + ": ERROR: Project with ID=" + str(project_id) +
                              " does not exist. Item not created."
                              )


def command_setduedate(args):

    try:
        item = set_item_duedate(item_id=args['id'], date_string=args['date'])
        write_result_and_exit(0, args, item,
                              par.prog + ": Due date set to " + str(item['date_string']) +
                              " for item with ID=" + str(item['id']) + "."
                              )
    except AttributeError:
        write_result_and_exit(1, args, None,
                              par.prog + ": ERROR: Item with ID=" + str(args['id']) +
                              " does not exist. Due date not set."
                              )


def command_setpriority(args):

    if args["id"] == "stdin":
        for line in fileinput.input("-"):
            args["id"] = line.strip("\n")
    if not isinstance(int(args["id"]),int):
        write_result_and_exit(1, args, None,
                              par.prog + ": ERROR: id argument is not an integer. Priority not set."
                              )

    try:
        item = set_item_priority(item_id=args['id'], priority=args['priority'])
        write_result_and_exit(0, args, item,
                              par.prog + ": Priority set to " + str(item['priority']) +
                              " for item with ID=" + str(item['id']) + "."
                              )
    except AttributeError:
        write_result_and_exit(1, args, None,
                              par.prog + ": ERROR: Item with ID=" + str(args['id']) +
                              " does not exist. Priority not set."
                              )


def command_addlabel(args):

    if args['id']:
        try:
            new_label = add_label(args['name'], args['id'])
            write_result_and_exit(0, args, new_label,
                                  par.prog + ": Label with name '" + str(new_label['name']) +
                                  "' and id " + str(new_label['id']) +
                                  " added to item with ID=" + str(args['id']) + "."
                                  )
        except AttributeError:
            write_result_and_exit(1, args, None,
                                  par.prog +
                                  " ERROR: Item with ID=" + str(args['id']) + " not found."
                                  )
    else:
        new_label = add_label(args['name'])
        write_result_and_exit(0, args, new_label,
                              par.prog + ": Label with name '" + str(new_label['name']) +
                              "' and id " + str(new_label['id']) + " added."
                              )


def command_addproject(args):

    new_project = add_project(name=args['name'], parent_project_id=args['id'])

    write_result_and_exit(0, args, new_project,
                          par.prog + ": Project (name:" + str(new_project['name']) +
                          ", id:" + str(new_project['id']) + ") added."
                          )


def command_removeproject(args):

    try:
        removed_project = remove_project(args['id'], args['delete'])
    except AttributeError:
        write_result_and_exit(1, args, None, par.prog + ": ERROR - Project not found.")
    except todoist.api.SyncError as err:
        write_result_and_exit(1, args, None, par.prog + ": ERROR - Todoist SyncError=" + pformat_todoist_obj(err.args))
    else:
        del_or_arc = " DELETED." if args["delete"] else " archived."
        write_result_and_exit(0, args, removed_project, par.prog + ": Project with ID=" + str(args['id']) + del_or_arc)


def command_addcomment(args):

    if args['file']:
        attachment_obj = upload_file(args['file'].name)
    else:
        attachment_obj = None

    try:
        new_comment = add_comment(args['text'], item_id=args['id'], attachment=attachment_obj)
        write_result_and_exit(0, args, new_comment,
                              par.prog + ": New comment created for item ID " + str(args['id']) +
                              " with ID=" + str(new_comment['id'])
                              )
    except todoist.api.SyncError:
        write_result_and_exit(1, args, None,
                              par.prog + ": ERROR - SyncError exception thrown."
                              )


def command_getprojectid(args):

    project_id_list = get_project_id_by_name(args['name'])

    if project_id_list:
        write_result_and_exit(0, args, project_id_list,
                              par.prog + ": Found project ID(s): " + str(project_id_list))
    else:
        write_result_and_exit(0, args, project_id_list,
                              par.prog + ": No projects found with name " + args['name'] + ".")


def command_getinfo(args):

    sync_response = get_sync_response()

    if args['key']:
        try:
            sync_response = sync_response[args['key']]
        except KeyError:
            write_result_and_exit(1, args, None,
                                  par.prog + " ERROR - " + args['key'] + " key not found."
                                  )

    write_result_and_exit(0, args, sync_response,
                          par.prog + ": getinfo(" + "key="+str(args['key']) + ")\n" +
                          str(pformat_todoist_obj(sync_response))
                          )


def command_notimplemented(args):

    print(par.prog, ": Command", args.command, "not yet implemented.")
    sys.exit(1)


if __name__ == "__main__":

    cargspar = argparse.ArgumentParser(add_help=False)
    cargspar.add_argument("--out", type=str, nargs="?", default=None, const="FULL", metavar="<key>",
                          help="write return object(s) to stdout. if <key> specified, limit to <key> value from return "
                               "object(s)")

    par = argparse.ArgumentParser(add_help=True)

    spars = par.add_subparsers(description='Sub-command description', dest='command', help='sub-command help')

    par_ai = spars.add_parser("additem", aliases=['ai'], parents=[cargspar],
                              help="create a new item, add to specified project id or Inbox"
                              )
    par_ai.add_argument("name", type=str, metavar="<itemname>", help="item name (enclose in quotes)")
    par_ai.add_argument("-i", "--id", type=int, metavar="<id>", help="project id")
    par_ai.set_defaults(func=command_additem)

    par_sdd = spars.add_parser("setduedate", aliases=['sdd'], parents=[cargspar], help="set item due date")
    par_sdd.add_argument("date", type=str, metavar="<date_string>")
    par_sdd.add_argument("-i", "--id", type=int, required=True, metavar="<id>", help="item id")
    par_sdd.set_defaults(func=command_setduedate)

    par_sp = spars.add_parser("setpriority", aliases=['sp'], parents=[cargspar], help="set item priority")
    par_sp.add_argument("priority", type=int, metavar="<priority>", help="item priority: 1-4, 1=low, 4=high")
    par_sp.add_argument("-i", "--id", type=str, metavar="<id>|stdin", help="item id (stdin=get id from stdin)")
    par_sp.set_defaults(func=command_setpriority)

    par_al = spars.add_parser("addlabel", aliases=['al'], parents=[cargspar],
                              help="create label, optionally add to item"
                              )
    par_al.add_argument("name", type=str, help="label name (will be created if it doesn't exist)")
    par_al.add_argument("-i", "--id", type=int, metavar="<id>", help="add label to this item id")
    par_al.set_defaults(func=command_addlabel)

    par_ac = spars.add_parser("addcomment", aliases=['ac'], parents=[cargspar], help="add comment to item or project")
    par_ac.add_argument("text", type=str, help="comment text")
    par_ac.add_argument("-f", "--file", type=argparse.FileType('r'), help="file to upload and attach to comment")
    par_ac.add_argument("-i", "--id", type=int, required=True, metavar="<id>", help="add comment to item or project id")
    par_ac.set_defaults(func=command_addcomment)

    par_ap = spars.add_parser("addproject", aliases=['ap'], parents=[cargspar], help="create project")
    par_ap.add_argument("name", type=str, help="project name")
    par_ap.add_argument("-i", "--id", type=int, metavar="<id>", help="parent project id")
    par_ap.set_defaults(func=command_addproject)

    par_rp = spars.add_parser("removeproject", aliases=['rp'], parents=[cargspar], help="remove project")
    par_rp.add_argument("-i", "--id", type=int, metavar="<id>", help="project id")
    par_rp.add_argument("-d", "--delete", action='store_true', help="delete (instead of archive)")
    par_rp.set_defaults(func=command_removeproject)

    par_gpi = spars.add_parser("getprojectid", aliases=['gpid'], parents=[cargspar], help="get project id(s) by name")
    par_gpi.add_argument("name", type=str, help="project name in quotes")
    par_gpi.set_defaults(func=command_getprojectid)

    par_gi = spars.add_parser("getinfo", aliases=['gi'], parents=[cargspar], help="get todoist data, options are ANDed")
    par_gi.add_argument("-k", "--key", type=str, metavar="<keyname>", help="get objects within <keyname> (e.g., items, "
                                                                           "projects, labels)")
    par_gi.set_defaults(func=command_getinfo)

    parsed_args = par.parse_args()
    if parsed_args.command:
        parsed_args.func(vars(parsed_args))
    else:
        par.print_usage()
