from inspect import signature
from typing import Tuple, List, Type, Any, TypeVar, Type
from abc import ABC

from .descriptor import SyncDescriptor
from .instantiate import IInstantiateService, ServiceIdentifier, IServiceAccessor
from .service_collection import ServiceCollection


_ENABLE_TRACING = True

T = TypeVar("T")
S = TypeVar("S", bound=ServiceIdentifier)


class InstantiateService(IInstantiateService):
    def __init__(
        self,
        _services: ServiceCollection = ServiceCollection([]),
        _strict: bool = False,
        _parent: IInstantiateService | None = None,
        _enable_tracing: bool = _ENABLE_TRACING,
    ):
        super().__init__()
        self._services = _services
        self._strict = _strict
        self._parent = _parent
        self._enable_tracing = _enable_tracing

        self._services.set(IInstantiateService, self)

    def _get_service_dependencies(self, descriptor: SyncDescriptor):
        sign = signature(descriptor.ctor)

        ret: List[Tuple[Type[ServiceIdentifier], int]] = []

        idx = 0
        for k, v in sign.parameters.items():
            annotation = v.annotation
            ret.append(annotation, idx)
            idx += 1

        return ret

    # Lazy proxy: https://code.activestate.com/recipes/578014-lazy-load-object-proxying/
    # Proxy: https://web.archive.org/web/20220819152103/http://code.activestate.com/recipes/496741-object-proxying/

    def create_instance(self, descriptor, *non_leading_service_args):

        if isinstance(descriptor, SyncDescriptor):
            service_dependencies = self._get_service_dependencies(descriptor)
            print(service_dependencies)
            service_args: List[Any] = []

            service_dependencies = sorted(
                service_dependencies, key=lambda dependency: dependency[1]
            )

            for dependency in service_dependencies:
                service_identifier, _ = dependency
                service = self._get_or_create_service_instance(service_identifier)
                service_args.append(service)

            args = descriptor.static_arguments + list(non_leading_service_args)
            first_service_arg_pos = (
                service_dependencies[0][0]
                if len(service_dependencies) > 0
                else len(args)
            )

            if len(args) != first_service_arg_pos:
                print(
                    "[createInstance] Service dependency error: ",
                    service_dependencies,
                    service_args,
                )

            final_args = args + service_args
            print(
                final_args,
                args,
                service_args,
                descriptor,
                descriptor.ctor,
                descriptor.static_arguments,
                descriptor.ctor(),
            )
            return descriptor.ctor(*tuple(final_args))

        else:
            raise Exception("Not implemented yet")

    def _get_or_create_service_instance(
        self, identifier: Type[T]
    ) -> T | SyncDescriptor[T]:
        instance = self._services.get(identifier)

        if isinstance(instance, SyncDescriptor):
            return self.create_instance(instance)
        else:
            return instance

    @property
    def service_accessor(self) -> IServiceAccessor:

        service_self = self

        class ServiceAccessor(IServiceAccessor):

            def get(self, descriptor: Type[T]) -> T:
                ret = service_self._get_or_create_service_instance(descriptor)
                return ret

        accessor = ServiceAccessor()

        return accessor
