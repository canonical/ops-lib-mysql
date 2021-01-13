Juju Operator Framework Charm Interface for MySQL & MariaDB Relations
=====================================================================

[![PyPI version](https://badge.fury.io/py/ops-lib-mysql.svg)](https://badge.fury.io/py/ops-lib-mysql)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/ops-lib-mysql.svg)](https://pypi.python.org/pypi/ops-lib-mysql/)
[![GitHub license](https://img.shields.io/github/license/canonical/ops-lib-mysql)](https://github.com/canonical/ops-lib-mysql/blob/master/LICENSE)
[![GitHub Actions (Tests)](https://github.com/canonical/ops-lib-mysql/workflows/Tests/badge.svg)](https://github.com/canonical/ops-lib-mysql/actions?query=workflow%3ATests)


To use this interface in your
[Juju Operator Framework](https://github.com/canonical/operator) charm,
instruct [charmcraft](https://github.com/canonical/charmcraft) to embed
it into your built Operator Framework charm by adding ops-lib-mysql to
your `requirements.txt` file::

```
ops
ops-lib-mysql
```

Your charm needs to declare its use of the interface in its `metadata.yaml` file:

```yaml
requires:
  db:
    interface: mysql
    limit: 1  # Most charms only handle a single MySQL Application.
```


Your charm needs to bootstrap it and handle events:

```python
from opslib.mysql import MySQLClient, MySQLRelationEvent


class MyCharm(ops.charm.CharmBase):
    _state = ops.framework.StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self._state.set_default(
            db_available=False, db_conn_str=None, db_host=None, db_port=None, db_name=None,
            db_user=None, db_password=None, db_root_password=None,
        )
        self.db = MySQLClient(self, 'db')  # 'db' relation in metadata.yaml
        self.framework.observe(self.db.on.database_changed, self._on_database_changed)

    def _on_database_changed(self, event: MySQLRelationEvent):
        self._state.db_available = event.is_available  # Boolean flag
        self._state.db_conn_str = event.connection_string  # host={host} port={port} ...
        self._state.db_host = event.host
        self._state.db_port = event.port
        self._state.db_name = event.database
        self._state.db_user = event.user
        self._state.db_password = event.password
        self._state.db_root_password = event.root_password
```
