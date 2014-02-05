from flaskApp import app
import logging
try:
    import MySQLdb
except ImportError as e:
    app.config['LOG_SQL'] = False


class LogLevel:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4


class Logger(object):
    """
    This class logs errors and warns to MySQL or text files.
    You can configure the log location inside of your config file
    
    USAGE:
    import Logger, LogLevel
    Logger.log(args**, LogLevel.ERROR)

    """
    _log_app = app.config.get('LOG_APP')
    _log_path = app.config.get('LOG_PATH')
    _logger = logging.getLogger(_log_app)
    _formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    _hdlr = logging.FileHandler(_log_path)
    _hdlr.setFormatter(_formatter)
    _logger.addHandler(_hdlr)
    _connection = None

    __author__ = 'James Irick'
    __credicts__ = 'James Irick'
    __license__ = 'GPL'
    __version__ = '0.0.1'
    __status__ = 'Production'
    __date__ = '3/24/2012'
    
    @staticmethod
    def _init_connection():
        try:
            Logger._connection = \
                    MySQLdb.connect(host=app.config.get('MYSQL_HOST'),
                                    user=app.config.get('MYSQL_USER'),
                                    passwd=app.config.get('MYSQL_PASSWD'),
                                    db=app.config.get('SPORTS_DB'), #LOGGER_DB
                                    connect_timeout=app.config.get('MYSQL_TIMEOUT'))
        except Exception as e:
            Logger._log_to_file("Log to SQL failed %s," % e.args, LogLevel.FATAL)
        Logger._is_init = True

    @staticmethod
    def log(msg=None, log_level=None):

        if msg and len(msg) > 0 and log_level:

            if app.config.get('LOG_SQL'):
                Logger._log_to_sql(msg, log_level)
            else:
                Logger._log_to_file(str(msg), log_level)

    @staticmethod
    def _log_to_file(msg=None, log_level=None):

        if LogLevel.DEBUG == log_level:
            Logger._logger.debug(msg)

        elif LogLevel.INFO == log_level:
            Logger._logger.error(msg)

        elif LogLevel.WARN == log_level:
            Logger._logger.warn(msg)

        elif LogLevel.ERROR == log_level:
            Logger._logger.error(msg)

        elif LogLevel.FATAL == log_level:
            Logger._logger.fatal(msg)
        else:
            pass
        return

    @staticmethod
    def _log_to_sql(msg=None, log_level=None):
        if not Logger._connection:
            Logger._init_connection()

        try:
            sql = ("call flaskdb.tbl_logs_add(%s,%s,%s)") % \
                Logger._connection.literal((log_level, msg[1], msg[0]))
            mysql_cursor = Logger._connection.cursor()
            mysql_cursor.execute(sql)
            mysql_cursor.close()
            mysql_cursor = Logger._connection.cursor()
            Logger._connection.commit()
            mysql_cursor.close()
            Logger._connection.close()

        except MySQLdb.Error as e:
            Logger._log_to_file(e.args, LogLevel.FATAL)

        except Exception as e:
            Logger._log_to_file(e.args, LogLevel.FATAL)

        return
