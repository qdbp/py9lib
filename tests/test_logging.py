from py9lib.log import get_logger


# noinspection PyMissingTypeHints
def test_basic():
    """
    Just checking we don't crash.
    """

    logger = get_logger('foo')
    logger.info('foo')
    logger.error('bar')
