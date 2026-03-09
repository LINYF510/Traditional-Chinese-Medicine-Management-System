"""Project package initialization."""

try:
    import pymysql
except ImportError:  # pragma: no cover
    pymysql = None

if pymysql is not None:
    pymysql.install_as_MySQLdb()
