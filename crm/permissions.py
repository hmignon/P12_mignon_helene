from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from .models import Event, Client, Contract


class IsManager(permissions.BasePermission):
    """ Grant all permissions to Management """

    def has_permission(self, request, view):
        if request.user.team != 'MANAGEMENT':
            pass
        return True


class ClientPermissions(permissions.BasePermission):
    """
        Sales team : can CREATE new clients / prospects
                     can VIEW and UPDATE any prospect and their own clients
        Support team : can VIEW their own clients
    """

    def has_permission(self, request, view):
        try:
            client = get_object_or_404(Client, id=view.kwargs['pk'])
            if request.user.team == 'SUPPORT' and request.method in permissions.SAFE_METHODS:
                return client in Client.objects.filter(contract__event__support_contact=request.user.id)
            elif request.user.team == 'SALES':
                return request.user == client.sales_contact

        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team == 'SALES'


class ContractPermissions(permissions.BasePermission):
    """
        Sales team : can CREATE new contracts
                     can VIEW and UPDATE contracts of their own clients if not signed
        Support team : can VIEW contracts of their own clients
    """

    def has_permission(self, request, view):
        try:
            contract = get_object_or_404(Contract, id=view.kwargs['pk'])
            if request.method in permissions.SAFE_METHODS:
                if request.user.team == 'SUPPORT':
                    return contract in Contract.objects.filter(event__support_contact=request.user.id)
                elif request.user.team == 'SALES':
                    return request.user == contract.sales_contact
            return request.user == contract.sales_contact and contract.status is False

        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team == 'SALES'


class EventPermissions(permissions.BasePermission):
    """
        Sales team : can CREATE new events
                     can VIEW events of their own clients
        Support team : can VIEW events of their own clients
                       can UPDATE events of their own clients if not finished
    """

    def has_permission(self, request, view):
        try:
            event = get_object_or_404(Event, id=view.kwargs['pk'])
            if request.method in permissions.SAFE_METHODS:
                if request.user.team == 'SALES':
                    return event in Event.objects.filter(contract__sales_contact=request.user)
                elif request.user.team == 'SUPPORT':
                    return event.support_contact == request.user
            return request.user == event.support_contact and event.event_status is False

        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team == 'SALES'
