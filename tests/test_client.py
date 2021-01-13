# This file is part of the ops-lib-mysql component for Juju Operator
# Framework Charms.
# Copyright 2020 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

from textwrap import dedent
import unittest

import ops.charm
import ops.lib
import ops.testing

from opslib import mysql


class Charm(ops.charm.CharmBase):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.db = mysql.MySQLClient(self, "db")

        self.framework.observe(self.db.on.database_changed, self.on_database_changed)
        self.database_changed_events = []

    def on_database_changed(self, event):
        self.database_changed_events.append(event)

    @property
    def last_database_changed_event(self):
        if self.database_changed_events:
            return self.database_changed_events[-1]
        return None


class TestMySQLClient(unittest.TestCase):
    def setUp(self):
        meta = dedent(
            """\
            name: dbclient
            requires:
              db:
                interface: mysql
                limit: 1
            """
        )
        self.harness = ops.testing.Harness(Charm, meta=meta)
        self.addCleanup(self.harness.cleanup)
        self.relation_id = self.harness.add_relation("db", "mysql")
        self.harness.add_relation_unit(self.relation_id, "mysql/0")

    def test_full(self):
        self.harness.begin()
        self.harness.update_relation_data(
            self.relation_id,
            "mysql/0",
            {
                "host": "hostname_or_addr",
                "port": "1234",
                "database": "dbname",
                "user": "username",
                "password": "s3cret",
                "root_password": "sup3r_s3cret",
            },
        )
        ev = self.harness.charm.last_database_changed_event
        self.assertIsNotNone(ev)
        self.assertEqual(ev.host, "hostname_or_addr")
        self.assertTrue(isinstance(ev.port, int))
        self.assertEqual(ev.port, 1234)
        self.assertEqual(ev.database, "dbname")
        self.assertEqual(ev.user, "username")
        self.assertEqual(ev.password, "s3cret")
        self.assertEqual(ev.root_password, "sup3r_s3cret")
        self.assertTrue(ev.is_available)
        self.assertEqual(
            ev.connection_string,
            "host=hostname_or_addr port=1234 dbname=dbname user=username password=s3cret root_password=sup3r_s3cret",
        )

    def test_default_port(self):
        self.harness.begin()
        self.harness.update_relation_data(
            self.relation_id,
            "mysql/0",
            {
                "host": "hostname_or_addr",
                "database": "dbname",
                "user": "username",
                "password": "s3cret",
                "root_password": "sup3r_s3cret",
            },
        )
        ev = self.harness.charm.last_database_changed_event
        self.assertIsNotNone(ev)
        self.assertTrue(isinstance(ev.port, int))
        self.assertEqual(ev.port, 3306)
        self.assertEqual(
            ev.connection_string,
            "host=hostname_or_addr port=3306 dbname=dbname user=username password=s3cret root_password=sup3r_s3cret",
        )

    def test_not_available(self):
        self.harness.begin()
        self.harness.update_relation_data(
            self.relation_id,
            "mysql/0",
            {
                "host": "hostname_or_addr",
                "database": "dbname",
                "user": "username",
                "password": "s3cret",
                "root_password": "sup3r_s3cret",
            },
        )
        ev = self.harness.charm.last_database_changed_event
        self.assertIsNotNone(ev)
        self.assertTrue(ev.is_available)
        self.assertEqual(
            ev.connection_string,
            "host=hostname_or_addr port=3306 dbname=dbname user=username password=s3cret root_password=sup3r_s3cret",
        )
        self.harness.update_relation_data(self.relation_id, "mysql/0", {"host": ""})
        ev2 = self.harness.charm.last_database_changed_event
        self.assertFalse(ev2.is_available)
        self.assertIsNone(ev2.connection_string)
