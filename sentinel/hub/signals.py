from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from guardian.models import Group as PermGroup
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user
from .models import Hub, Leaf, Condition, Datastore
import re


def create_hub_permission_group(sender, **kwargs):
    if kwargs.get('created', False):
        if not PermGroup.objects.filter(name="default").exists():
            default_group = PermGroup.objects.create(name="default")
        default_group = PermGroup.objects.get(name="default")
        hub = kwargs['instance']
        hub_group = PermGroup.objects.create(name="hub-" + str(hub.id))
        assign_perm('view_hub', hub_group, hub)
        assign_perm('delete_hub', hub_group, hub)
        remove_perm('view_hub', default_group, hub)
        remove_perm('delete_hub', default_group, hub)


def create_leaf_permissions(sender, **kwargs):
    if kwargs.get('created', False):
        leaf = kwargs['instance']
        hub_group = PermGroup.objects.get(name="hub-" + str(leaf.hub.id))
        default_group = PermGroup.objects.get(name="default")
        assign_perm('view_leaf', hub_group, leaf)
        assign_perm('change_leaf', hub_group, leaf)
        assign_perm('delete_leaf', hub_group, leaf)
        remove_perm('view_leaf', default_group, leaf)
        remove_perm('change_leaf', default_group, leaf)
        remove_perm('delete_leaf', default_group, leaf)


def create_user_default_permissions(sender, **kwargs):
    user = kwargs['instance']
    if kwargs.get('created', False) and user.username != 'AnonymousUser' and user.username != AnonymousUser.username:
        if not PermGroup.objects.filter(name="default").exists():
            default_group = PermGroup.objects.create(name="default")
        default_group = PermGroup.objects.get(name="default")

        user.groups.add(default_group)
        leaf_pattern = r"[0-9]+-[0-9a-f]{8}(?:-{0,1}[0-9a-f]{4}){3}-{0,1}[0-9a-f]{12}"
        if not re.match(leaf_pattern, user.username):
            assign_perm('hub.add_hub', user)
            assign_perm('hub.delete_hub', user)


def create_datastore_permissions(sender, **kwargs):
    if kwargs.get('created', False):
        datastore = kwargs['instance']
        hub_group = PermGroup.objects.get(name="hub-" + str(datastore.hub.id))
        assign_perm('view_datastore', hub_group, datastore)
        assign_perm('delete_datastore', hub_group, datastore)


def create_condition_permissions(sender, **kwargs):
    if kwargs.get('created', False):
        condition = kwargs['instance']
        hub_group = PermGroup.objects.get(name="hub-" + str(condition.hub.id))
        default_group = PermGroup.objects.get(name="default")
        assign_perm('view_condition', hub_group, condition)
        remove_perm('view_condition', default_group, condition)
        assign_perm('delete_condition', hub_group, condition)
        remove_perm('delete_condition', default_group, condition)


def delete_leaf_user(sender, **kwargs):
    leaf = kwargs['instance']
    if User.objects.filter(username=f"{leaf.hub.id}-{leaf.uuid}").exists():
        User.objects.get(username=f"{leaf.hub.id}-{leaf.uuid}").delete()


post_save.connect(create_hub_permission_group, sender=Hub)
post_save.connect(create_leaf_permissions, sender=Leaf)
post_save.connect(create_user_default_permissions, sender=User)
post_save.connect(create_datastore_permissions, sender=Datastore)
post_save.connect(create_condition_permissions, sender=Condition)
pre_delete.connect(delete_leaf_user, sender=Leaf)
