from abc import ABC, abstractmethod
from typing import TypeVar, Any, Type, Iterable, MutableMapping, Generic


T = TypeVar("T")


class IServiceAccessor(ABC):
    @abstractmethod
    def get(self, descriptor: Type[T]) -> T:
        pass


"""
#region: TODO: Add service identifier decorator on head of Interface classes
See instantiate_service.py:InstantiateService._get_service_dependencies it is now using 'Type[ABC]' for service identification. This should be changed to _Utils.service_ids.get()
"""


A = TypeVar("A", bound=ABC)


class ServiceIdentifier(Generic[T]):
    pass


class _Util:
    service_ids: MutableMapping[str, Type[ServiceIdentifier[Any]]] = {}


def service_identifier(identifier: str):

    def wrapper[T](cls: Type[T]) -> Type[T]:
        _Util.service_ids[cls.__name__] = cls
        return cls

    return wrapper


# endregion


@service_identifier("IInstantiateService")
class IInstantiateService(ServiceIdentifier):

    @abstractmethod
    def create_instance(
        self, descriptor: Type[T], *non_leading_service_args: Iterable[Any]
    ) -> T:
        pass

    @property
    @abstractmethod
    def service_accessor(self) -> IServiceAccessor:
        pass
