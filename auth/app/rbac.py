r"""
resource permission policy types
- personal
    * role permissions:
        - owner: control, read, write
        - other: none / read
        
- group (to resource instance)
    * role permissions:
        - owner: control, read, write
        - edit: read, write
        - view: read
        - other: none
"""

from casbin import Enforcer
from pydantic import BaseModel
from fastapi import Depends, HTTPException, APIRouter, Query
from typing import Any, Dict, List, Optional
from fastapi_users.schemas import BaseUser


class UserRole(BaseModel):
    user: Any
    role: str


class InstanceGroupPolicy:
    roles = ['owner', 'view', 'edit']
    permissions = {
        'owner': 'control|read|write',
        'edit': 'read|write',
        'view': 'read',
    }
    default_role = 'edit'

    def __init__(self,
            enforcer: Enforcer,
            resource_name: str,
            resource_key: str = 'uid',
            can_assign_owner: bool = True,
            default_role: str = 'edit',
            check_superuser: bool = True,
            ):
        if resource_name == 'user':
            raise ValueError('resource_name cannot be user')
        if default_role not in self.roles:
            raise ValueError(f'Invalid default_role. Expect {self.roles}')

        self.enforcer = enforcer
        self.resource_name = resource_name
        self.resource_key = resource_key
        self.can_assign_owner = can_assign_owner
        self.default_role = default_role
        self.check_superuser = check_superuser

    def has_permission(self,
            user: BaseUser,
            uid: int,
            action: str = 'read',
            ) -> bool:
        resource = f'{self.resource_name}-{uid}'
        if self.check_superuser and user.is_superuser:
            return True
        return self.enforcer.enforce(str(user.id), resource, 'read')

    def add_permission(self,
            user: BaseUser,
            uid: int,
            ):
        resource = f'{self.resource_name}-{uid}'
        self.enforcer.add_role_for_user(str(user.id), f'{resource}-owner')
        for role, permission in self.permissions.items():
            self.enforcer.add_permission_for_user(f'{resource}-{role}', resource, permission)

    def check_permission(self,
            get_current_user: 'DependencyCallable',
            action,
            ) -> 'DependencyCallable':
        async def _get_data(
                uid: int,
                user: BaseUser = Depends(get_current_user),
                ):
            if self.has_permission(user, uid, action):
                yield uid
            else:
                raise HTTPException(403, detail='Permission Deny')
        return _get_data

    def get_router(self,
            get_current_user: 'DependencyCallable',
            get_user: 'DependencyCallable',
            # resource_key: str = 'uid',
            instance_path: str,
            router: Optional[APIRouter] = None,
            router_kwargs: dict = dict(),
            ):
        if router is None:
            router = APIRouter(**router_kwargs)

        # def _getpath(path):
            # return '/{'+self.resource_key+'}'+path

        # def _getpath(path):
            # return '/{'+resource_key+'}'+path

        def _getpath(path):
            return instance_path+path

        async def _get_resource(
                uid: int = Depends(self.check_permission(get_current_user, 'control')),
                ):
            yield f'{self.resource_name}-{uid}'

        async def _get_user_id(
                user: BaseUser = Depends(get_user),
                current_user: BaseUser = Depends(get_current_user),
                ):
            if self.check_superuser and current_user.is_superuser: # TODO
                yield str(user.id)
            elif str(user.id) != str(current_user.id):
                yield str(user.id)
            else:
                raise HTTPException(406, 'Target user cannot be self')

        regex = '^(%s)$' % '|'.join([r for r in self.roles if self.can_assign_owner or r != 'owner'])

        @router.get(_getpath('/user'), response_model=List[UserRole])
        async def get_resource_users(
                resource: str = Depends(_get_resource),
                ):
            users = [
                {'user': user_id, 'role': role}
                for role in self.roles
                for user_id in self.enforcer.get_users_for_role(f'{resource}-{role}')
            ]
            return users

        @router.post(_getpath('/user'))
        async def add_resource_user(
                user_id: str = Depends(_get_user_id),
                resource: str = Depends(_get_resource),
                role: str = Query(self.default_role, regex=regex)
                ):
            if self.enforcer.enforce(user_id, resource, 'read'):
                raise HTTPException(406, detail=f'{user_id} is already a member')
            return self.enforcer.add_role_for_user(user_id, f'{resource}-{role}')

        @router.patch(_getpath('/user'))
        async def update_resource_user(
                user_id: str = Depends(_get_user_id),
                resource: str = Depends(_get_resource),
                role: Optional[str] = Query(None, regex=regex)
                ):
            if role is None:
                return False
            if not self.enforcer.enforce(user_id, resource, 'read'):
                raise HTTPException(406, detail=f'{user_id} is not a member')

            if self.enforcer.has_role_for_user(user_id, f'{resource}-{role}'):
                return False
            for _role in self.roles:
                if _role == role:
                    self.enforcer.add_role_for_user(user_id, f'{resource}-{_role}')
                else:
                    self.enforcer.delete_role_for_user(user_id, f'{resource}-{_role}')
            return True

        @router.delete(_getpath('/user'))
        async def delete_resource_user(
                user_id: str = Depends(_get_user_id),
                resource: str = Depends(_get_resource),
                ):
            if not self.enforcer.enforce(user_id, resource, 'read'):
                raise HTTPException(406, detail=f'{user_id} is not a member')

            succ = False
            for role in self.roles:
                succ |= self.enforcer.delete_role_for_user(user_id, f'{resource}-{role}')
            return succ
        return router
