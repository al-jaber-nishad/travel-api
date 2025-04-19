from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
	""" Allows access only to admin users """
	def has_permission(self, request, view):
		return bool(request.user.is_authenticated and request.user.is_admin)


def is_adminuser(view_func):
	def wrapper(request, *args, **kwargs):
		print('request.user: ', request.user)
		print('args: ', args)
		print('kwargs: ', kwargs)
		if request.user.is_admin:
			return view_func(request, *args, **kwargs)
		else:
			return Response({'detail': "Only admin can perform this operation."}, status=status.HTTP_403_FORBIDDEN)
	return wrapper


def has_permissions(allowed_permissions=[]):
	def decorator(view_func):
		def wrap(request, *args, **kwargs):
			if type(request.user) is not AnonymousUser:
				user = request.user
				role = user.role
				permissions = role.permissions.all()

				if user.is_admin:
					return view_func(request, *args, **kwargs)

				for permission in allowed_permissions:
					if permissions.filter(name=permission).exists():
						# print("Permission =====>", permission)
						return view_func(request, *args, **kwargs)
				else:
					return Response({'detail': f"You don't have these permissions {allowed_permissions}"})
			else:
				return Response({'detail': "Authentication credentials were not provided."})
		return wrap
	return decorator
