from landscape.schema import (
    Message, KeyDict, Dict, List, Tuple,
    Bool, Int, Float, String, Unicode, UnicodeOrString, Constant,
    Any)

# When adding a new schema, which deprecates an older schema, the recommended
# naming convention, is to name it SCHEMA_NAME_ and the last API version that
# the schema works with.
#
# i.e. if I have USERS and I'm deprecating it, in API 2.2, then USERS becomes
# USERS_2_1

utf8 = UnicodeOrString("utf-8")

process_info = KeyDict({"pid": Int(),
                        "name": utf8,
                        "state": String(),
                        "sleep-average": Int(),
                        "uid": Int(),
                        "gid": Int(),
                        "vm-size": Int(),
                        "start-time": Int(),
                        "percent-cpu": Float()},
                       # Optional for backwards compatibility
                       optional=["vm-size", "sleep-average", "percent-cpu"])

ACTIVE_PROCESS_INFO = Message(
    "active-process-info",
    {"kill-processes": List(Int()),
     "kill-all-processes": Bool(),
     "add-processes": List(process_info),
     "update-processes": List(process_info)
     },
    # XXX Really we don't want all three of these keys to be optional:
    # we always want _something_...
    optional=["add-processes", "update-processes", "kill-processes",
              "kill-all-processes"])

COMPUTER_UPTIME = Message(
    "computer-uptime",
    {"startup-times": List(Int()),
     "shutdown-times": List(Int())},
    # XXX Again, one or the other.
    optional=["startup-times", "shutdown-times"])

CLIENT_UPTIME = Message(
    "client-uptime",
    {"period": Tuple(Float(), Float()),
     "components": List(Int())},
    optional=["components"]) # just for backwards compatibility

OPERATION_RESULT = Message(
    "operation-result",
    {"operation-id": Int(),
     "status": Int(),
     "result-code": Int(),
     "result-text": utf8},
    optional=["result-code", "result-text"])

#ACTION_INFO is obsolete.
ACTION_INFO = Message(
    "action-info",
    {"response-id": Int(),
     "success": Bool(),
     "kind": String(),
     "parameters": String()})

COMPUTER_INFO = Message(
    "computer-info",
    {"hostname": utf8,
     "total-memory": Int(),
     "total-swap": Int()},
    # Not sure why these are all optional, but it's explicitly tested
    # in the server
    optional=["hostname", "total-memory", "total-swap"])

DISTRIBUTION_INFO = Message(
    "distribution-info",
    {"distributor-id": utf8,
     "description": utf8,
     "release": utf8,
     "code-name": utf8},
    # all optional because the lsb-release file may not have all data.
    optional=["distributor-id", "description", "release", "code-name"])


hal_data = Dict(Unicode(),
                Any(Unicode(), List(Unicode()), Bool(), Int(), Float()))

HARDWARE_INVENTORY = Message("hardware-inventory", {
    "devices": List(Any(Tuple(Constant("create"), hal_data),
                        Tuple(Constant("update"),
                              Unicode(), # udi,
                              hal_data, # creates,
                              hal_data, # updates,
                              hal_data), # deletes
                        Tuple(Constant("delete"),
                              Unicode()),
                        ),
                    )
    })


LOAD_AVERAGE = Message("load-average", {
    "load-averages": List(Tuple(Int(), Float())),
    })


MEMORY_INFO = Message("memory-info", {
    "memory-info": List(Tuple(Float(), Int(), Int())),
    })

RESYNCHRONIZE = Message(
    "resynchronize",
    {"operation-id": Int()},
    # operation-id is only there if it's a response to a server-initiated
    # resynchronize.
    optional=["operation-id"])

MOUNT_ACTIVITY = Message("mount-activity", {
    "activities": List(Tuple(Float(), utf8, Bool()))
    })

MOUNT_INFO = Message("mount-info", {
    "mount-info": List(Tuple(Float(),
                             KeyDict({"mount-point": utf8,
                                      "device": utf8,
                                      "filesystem": utf8,
                                      "total-space": Int()}),
                             )),
    })

FREE_SPACE = Message("free-space", {
    "free-space": List(Tuple(Float(), utf8, Int()))
    })


REGISTER = Message(
    "register",
    {"registration_password": Any(utf8, Constant(None)),
     "computer_title": utf8,
     "hostname": utf8,
     "account_name": utf8},
    # hostname wasn't around in old versions
    optional=["registration_password", "hostname"])

TEMPERATURE = Message("temperature", {
    "thermal-zone": utf8,
    "temperatures": List(Tuple(Int(), Float())),
    })

PROCESSOR_INFO = Message(
    "processor-info",
    {"processors": List(KeyDict({"processor-id": Int(),
                                 "vendor": utf8,
                                 "model": utf8,
                                 "cache-size": Int(),
                                 },
                                optional=["vendor", "cache-size"])),
    })

user_data = KeyDict({
    "uid": Int(),
    "username": utf8,
    "name": Any(utf8, Constant(None)),
    "enabled": Bool(),
    "location": Any(utf8, Constant(None)),
    "home-phone": Any(utf8, Constant(None)),
    "work-phone": Any(utf8, Constant(None)),
    "primary-gid": Any(Int(), Constant(None)),
    "primary-groupname": utf8},
    optional=["primary-groupname", "primary-gid"]
    )

group_data = KeyDict({
    "gid": Int(),
    "name": utf8
    })

USERS = Message(
    "users",
    {"operation-id": Int(),
     "create-users": List(user_data),
     "update-users": List(user_data),
     "delete-users": List(utf8),
     "create-groups": List(group_data),
     "update-groups": List(group_data),
     "delete-groups": List(utf8),
     "create-group-members": Dict(utf8, List(utf8)),
     "delete-group-members": Dict(utf8, List(utf8)),
     },
    # operation-id is only there for responses, and all other are
    # optional as long as one of them is there (no way to say that yet)
    optional=["operation-id", "create-users", "update-users", "delete-users",
              "create-groups", "update-groups", "delete-groups",
              "create-group-members", "delete-group-members"])

USERS_2_1 = Message(
    "users",
    {"operation-id": Int(),
     "create-users": List(user_data),
     "update-users": List(user_data),
     "delete-users": List(Int()),
     "create-groups": List(group_data),
     "update-groups": List(group_data),
     "delete-groups": List(Int()),
     "create-group-members": Dict(Int(), List(Int())),
     "delete-group-members": Dict(Int(), List(Int())),
     },
    # operation-id is only there for responses, and all other are
    # optional as long as one of them is there (no way to say that yet)
    optional=["operation-id", "create-users", "update-users", "delete-users",
              "create-groups", "update-groups", "delete-groups",
              "create-group-members", "delete-group-members"])

USERS_2_0 = Message(
    "users",
    {"operation-id": Int(),
     "create-users": List(user_data),
     "update-users": List(user_data),
     "delete-users": List(Int()),
     "create-groups": List(group_data),
     "update-groups": List(group_data),
     "delete-groups": List(Int()),
     "create-group-members": Dict(Int(), List(Int())),
     "delete-group-members": Dict(Int(), List(Int())),
     },
    # operation-id is only there for responses, and all other are
    # optional as long as one of them is there (no way to say that yet)
    optional=["operation-id", "create-users", "update-users", "delete-users",
              "create-groups", "update-groups", "delete-groups",
              "create-group-members", "delete-group-members"])

opt_str = Any(utf8, Constant(None))
OLD_USERS = Message(
    "users",
    {"users": List(KeyDict({"username": utf8,
                            "uid": Int(),
                            "realname": opt_str,
                            "location": opt_str,
                            "home-phone": opt_str,
                            "work-phone": opt_str,
                            "enabled": Bool()},
                           optional=["location", "home-phone", "work-phone"])),
     "groups": List(KeyDict({"gid": Int(),
                             "name": utf8,
                             "members": List(utf8)}))
     },
    optional=["groups"])

package_ids_or_ranges = List(Any(Tuple(Int(), Int()), Int()))
PACKAGES = Message(
    "packages",
    {"installed": package_ids_or_ranges,
     "available": package_ids_or_ranges,
     "available-upgrades": package_ids_or_ranges,
     "not-installed": package_ids_or_ranges,
     "not-available": package_ids_or_ranges,
     "not-available-upgrades": package_ids_or_ranges},
    optional=["installed", "available", "available-upgrades",
              "not-available", "not-installed", "not-available-upgrades"])

CHANGE_PACKAGES_RESULT = Message(
    "change-packages-result",
    {"operation-id": Int(),
     "must-install": List(Any(Int(), Constant(None))),
     "must-remove": List(Any(Int(), Constant(None))),
     "result-code": Int(),
     "result-text": utf8},
    optional=["result-text", "must-install", "must-remove"])

UNKNOWN_PACKAGE_HASHES = Message("unknown-package-hashes", {
    "hashes": List(String()),
    "request-id": Int(),
    })

ADD_PACKAGES = Message("add-packages", {
    "packages": List(KeyDict({"name": utf8,
                              "description": Unicode(),
                              "section": Unicode(),
                              "relations": List(Tuple(Int(), utf8)),
                              "summary": Unicode(),
                              "installed-size":  Any(Int(), Constant(None)),
                              "size":  Any(Int(), Constant(None)),
                              "version": utf8,
                              "type": Int(),
                              })),
    "request-id": Int(),
    })

TEXT_MESSAGE = Message("text-message", {
    "message": Unicode()
    })

TEST = Message(
    "test",
    {"greeting": String(),
     "consistency-error": Bool(),
     "echo": String(),
     "sequence": Int()},
    optional=["greeting", "consistency-error", "echo", "sequence"])

CUSTOM_GRAPH = Message("custom-graph", {
    # The tuples are timestamp, value
    "graph-data": List(KeyDict({"graph-id": Int(),
                                "data": List(Tuple(Float(), Float()))})),
    # Tuple of graph-id, error-message
    "error-messages": List(Tuple(Int(), Unicode()))},
    optional=["error-messages"]
    )

message_schemas = {}
for schema in [ACTIVE_PROCESS_INFO, COMPUTER_UPTIME, CLIENT_UPTIME,
               OPERATION_RESULT, COMPUTER_INFO, DISTRIBUTION_INFO,
               HARDWARE_INVENTORY, LOAD_AVERAGE, MEMORY_INFO,
               RESYNCHRONIZE, MOUNT_ACTIVITY, MOUNT_INFO, FREE_SPACE,
               REGISTER, TEMPERATURE, PROCESSOR_INFO, USERS, PACKAGES,
               CHANGE_PACKAGES_RESULT, UNKNOWN_PACKAGE_HASHES,
               ADD_PACKAGES, TEXT_MESSAGE, TEST, CUSTOM_GRAPH]:
    message_schemas[schema.type] = schema
