from django.urls import path
from .views import (MessageSendView, MessageQueryByPageView, MessageDeleteView, MessageMineView, MessageReadView, StatsDashboardView,
    UserQueryByPageView, UserInsertOrUpdateView, UserSaveView, UserDeleteView,
    RoleQueryByPageView, RoleSaveView, RoleDeleteView, RoleMenuAddView, RoleMenuQueryView, MenuTreeView, MenuSaveView, MenuDeleteView,
    DeptQueryByPageView, DeptTreeView, DeptSaveView, DeptDeleteView,
    DictTypeQueryView, DictDataQueryView, DictDataByTypeView,
    NoticeQueryView, NoticeSaveView, NoticeDeleteView, NewsQueryView, BannerQueryView, BannerSaveView, BannerUploadView, BannerDeleteView, BannerLoadView,
    LoginInfoQueryView, OperLogQueryView
)

urlpatterns = [
    path('user/queryByPage', UserQueryByPageView.as_view()),
    path('user/insertOrUpdate', UserInsertOrUpdateView.as_view()),
    path('user/save', UserSaveView.as_view()),
    path('user/delete/<int:user_id>', UserDeleteView.as_view()),
    path('user/delete', UserDeleteView.as_view()),

    path('role/queryByPage', RoleQueryByPageView.as_view()),
    path('role/save', RoleSaveView.as_view()),
    path('role/delete/<int:role_id>', RoleDeleteView.as_view()),
    path('role/delete', RoleDeleteView.as_view()),
    path('role/roleMenu/add', RoleMenuAddView.as_view()),
    path('role/roleMenu/query', RoleMenuQueryView.as_view()),
    path('menu/queryTreeDataByUserId', MenuTreeView.as_view()),
    path('menu/save', MenuSaveView.as_view()),
    path('menu/delete/<int:menu_id>', MenuDeleteView.as_view()),
    path('menu/delete', MenuDeleteView.as_view()),

    path('dept/queryByPage', DeptQueryByPageView.as_view()),
    path('dept/tree', DeptTreeView.as_view()),
    path('dept/save', DeptSaveView.as_view()),
    path('dept/delete/<int:dept_id>', DeptDeleteView.as_view()),
    path('dept/delete', DeptDeleteView.as_view()),

    path('dictType/queryByPage', DictTypeQueryView.as_view()),
    path('dictData/queryByPage', DictDataQueryView.as_view()),
    path('dictData/type/<str:dict_type>', DictDataByTypeView.as_view()),

    path('notice/queryByPage', NoticeQueryView.as_view()),
    path('notice/save', NoticeSaveView.as_view()),
    path('notice/delete/<int:notice_id>', NoticeDeleteView.as_view()),
    path('notice/delete', NoticeDeleteView.as_view()),
    path('news/queryByPage', NewsQueryView.as_view()),
    path('banner/queryByPage', BannerQueryView.as_view()),
    path('banner/save', BannerSaveView.as_view()),
    path('banner/upload', BannerUploadView.as_view()),
    path('banner/delete/<int:id>', BannerDeleteView.as_view()),
    path('banner/delete', BannerDeleteView.as_view()),
    path('banner/loadBanner', BannerLoadView.as_view()),

    path('loginInfo/queryByPage', LoginInfoQueryView.as_view()),
    path('operLog/queryByPage', OperLogQueryView.as_view()),

    path('message/send', MessageSendView.as_view()),
    path('message/queryByPage', MessageQueryByPageView.as_view()),
    path('message/delete/<str:message_id>', MessageDeleteView.as_view()),
    path('message/delete', MessageDeleteView.as_view()),
    path('message/queryMine', MessageMineView.as_view()),
    path('message/read', MessageReadView.as_view()),
    path('stats/dashboard', StatsDashboardView.as_view()),
]
