# from typing import List, Self
#
# from pydantic import BaseModel
#
# # from app.models.user import User
#
#
# class UsersDetailResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#
#     class Config:
#         from_attributes = True
#
#
# class UsersResponse(BaseModel):
#     users: List[UsersDetailResponse]
#
#     @classmethod
#     def from_orm(cls, users: List[User]) -> Self:
#         return cls(
#             users=[UsersDetailResponse(**user.__dict__) for user in users]
#         )
