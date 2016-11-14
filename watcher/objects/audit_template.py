# -*- encoding: utf-8 -*-
# Copyright 2013 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An :ref:`Audit <audit_definition>` may be launched several times with the same
settings (:ref:`Goal <goal_definition>`, thresholds, ...). Therefore it makes
sense to save those settings in some sort of Audit preset object, which is
known as an :ref:`Audit Template <audit_template_definition>`.

An :ref:`Audit Template <audit_template_definition>` contains at least the
:ref:`Goal <goal_definition>` of the :ref:`Audit <audit_definition>`.

It may also contain some error handling settings indicating whether:

-  :ref:`Watcher Applier <watcher_applier_definition>` stops the
   entire operation
-  :ref:`Watcher Applier <watcher_applier_definition>` performs a rollback

and how many retries should be attempted before failure occurs (also the latter
can be complex: for example the scenario in which there are many first-time
failures on ultimately successful :ref:`Actions <action_definition>`).

Moreover, an :ref:`Audit Template <audit_template_definition>` may contain some
settings related to the level of automation for the
:ref:`Action Plan <action_plan_definition>` that will be generated by the
:ref:`Audit <audit_definition>`.
A flag will indicate whether the :ref:`Action Plan <action_plan_definition>`
will be launched automatically or will need a manual confirmation from the
:ref:`Administrator <administrator_definition>`.

Last but not least, an :ref:`Audit Template <audit_template_definition>` may
contain a list of extra parameters related to the
:ref:`Strategy <strategy_definition>` configuration. These parameters can be
provided as a list of key-value pairs.
"""

from watcher.common import exception
from watcher.common import utils
from watcher.db import api as db_api
from watcher import objects
from watcher.objects import base
from watcher.objects import fields as wfields


@base.WatcherObjectRegistry.register
class AuditTemplate(base.WatcherPersistentObject, base.WatcherObject,
                    base.WatcherObjectDictCompat):

    # Version 1.0: Initial version
    # Version 1.1: Added 'goal' and 'strategy' object field
    VERSION = '1.1'

    dbapi = db_api.get_instance()

    fields = {
        'id': wfields.IntegerField(),
        'uuid': wfields.UUIDField(),
        'name': wfields.StringField(),
        'description': wfields.StringField(nullable=True),
        'scope': wfields.FlexibleListOfDictField(nullable=True),
        'goal_id': wfields.IntegerField(),
        'strategy_id': wfields.IntegerField(nullable=True),

        'goal': wfields.ObjectField('Goal', nullable=True),
        'strategy': wfields.ObjectField('Strategy', nullable=True),
    }

    object_fields = {
        'goal': (objects.Goal, 'goal_id'),
        'strategy': (objects.Strategy, 'strategy_id'),
    }

    @base.remotable_classmethod
    def get(cls, context, audit_template_id, eager=False):
        """Find an audit template based on its id or uuid

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: AuditTemplate(context)
        :param audit_template_id: the id *or* uuid of a audit_template.
        :param eager: Load object fields if True (Default: False)
        :returns: a :class:`AuditTemplate` object.
        """
        if utils.is_int_like(audit_template_id):
            return cls.get_by_id(context, audit_template_id, eager=eager)
        elif utils.is_uuid_like(audit_template_id):
            return cls.get_by_uuid(context, audit_template_id, eager=eager)
        else:
            raise exception.InvalidIdentity(identity=audit_template_id)

    @base.remotable_classmethod
    def get_by_id(cls, context, audit_template_id, eager=False):
        """Find an audit template based on its integer id

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: AuditTemplate(context)
        :param audit_template_id: the id of a audit_template.
        :param eager: Load object fields if True (Default: False)
        :returns: a :class:`AuditTemplate` object.
        """
        db_audit_template = cls.dbapi.get_audit_template_by_id(
            context, audit_template_id, eager=eager)
        audit_template = cls._from_db_object(
            cls(context), db_audit_template, eager=eager)
        return audit_template

    @base.remotable_classmethod
    def get_by_uuid(cls, context, uuid, eager=False):
        """Find an audit template based on uuid

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: AuditTemplate(context)
        :param uuid: the uuid of a audit_template.
        :param eager: Load object fields if True (Default: False)
        :returns: a :class:`AuditTemplate` object.
        """
        db_audit_template = cls.dbapi.get_audit_template_by_uuid(
            context, uuid, eager=eager)
        audit_template = cls._from_db_object(
            cls(context), db_audit_template, eager=eager)
        return audit_template

    @base.remotable_classmethod
    def get_by_name(cls, context, name, eager=False):
        """Find an audit template based on name

        :param name: the logical name of a audit_template.
        :param context: Security context
        :param eager: Load object fields if True (Default: False)
        :returns: a :class:`AuditTemplate` object.
        """
        db_audit_template = cls.dbapi.get_audit_template_by_name(
            context, name, eager=eager)
        audit_template = cls._from_db_object(
            cls(context), db_audit_template, eager=eager)
        return audit_template

    @base.remotable_classmethod
    def list(cls, context, filters=None, limit=None, marker=None,
             sort_key=None, sort_dir=None, eager=False):
        """Return a list of :class:`AuditTemplate` objects.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: AuditTemplate(context)
        :param filters: dict mapping the filter key to a value.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param eager: Load object fields if True (Default: False)
        :returns: a list of :class:`AuditTemplate` object.
        """
        db_audit_templates = cls.dbapi.get_audit_template_list(
            context,
            filters=filters,
            limit=limit,
            marker=marker,
            sort_key=sort_key,
            sort_dir=sort_dir,
            eager=eager)

        return [cls._from_db_object(cls(context), obj, eager=eager)
                for obj in db_audit_templates]

    @base.remotable
    def create(self):
        """Create a :class:`AuditTemplate` record in the DB

        :returns: An :class:`AuditTemplate` object.
        """
        values = self.obj_get_changes()
        db_audit_template = self.dbapi.create_audit_template(values)
        # Note(v-francoise): Always load eagerly upon creation so we can send
        # notifications containing information about the related relationships
        self._from_db_object(self, db_audit_template, eager=True)

    def destroy(self):
        """Delete the :class:`AuditTemplate` from the DB"""
        self.dbapi.destroy_audit_template(self.uuid)
        self.obj_reset_changes()

    @base.remotable
    def save(self):
        """Save updates to this :class:`AuditTemplate`.

        Updates will be made column by column based on the result
        of self.what_changed().
        """
        updates = self.obj_get_changes()
        self.dbapi.update_audit_template(self.uuid, updates)

        self.obj_reset_changes()

    @base.remotable
    def refresh(self, eager=False):
        """Loads updates for this :class:`AuditTemplate`.

        Loads a audit_template with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded audit_template column by column, if there are any updates.
        :param eager: Load object fields if True (Default: False)
        """
        current = self.get_by_uuid(self._context, uuid=self.uuid, eager=eager)
        self.obj_refresh(current)

    @base.remotable
    def soft_delete(self):
        """Soft Delete the :class:`AuditTemplate` from the DB"""
        self.dbapi.soft_delete_audit_template(self.uuid)
