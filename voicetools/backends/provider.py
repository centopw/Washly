from voicetools.config import settings

_mock_booking = None
_mock_shop = None
_mock_user = None


def get_booking_backend():
    if settings.backend == "mongo":
        from voicetools.backends.mongo_bookings import MongoBookingBackend
        return MongoBookingBackend()
    global _mock_booking
    if _mock_booking is None:
        from voicetools.backends.bookings import MockBookingBackend
        _mock_booking = MockBookingBackend()
    return _mock_booking


def get_shop_backend():
    if settings.backend == "mongo":
        from voicetools.backends.mongo_shops import MongoShopBackend
        return MongoShopBackend()
    global _mock_shop
    if _mock_shop is None:
        from voicetools.backends.shops import MockShopBackend
        _mock_shop = MockShopBackend(booking_backend=get_booking_backend())
    return _mock_shop


def get_user_backend():
    if settings.backend == "mongo":
        from voicetools.backends.mongo_users import MongoUserBackend
        return MongoUserBackend()
    global _mock_user
    if _mock_user is None:
        from voicetools.backends.users import MockUserBackend
        _mock_user = MockUserBackend()
    return _mock_user


def reset_mock_backends() -> None:
    """Reset singleton mocks -- for testing."""
    global _mock_booking, _mock_shop, _mock_user
    _mock_booking = None
    _mock_shop = None
    _mock_user = None
