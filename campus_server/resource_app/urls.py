from django.urls import path
from .views import BuildingQueryByPageView, BuildingSaveView, BuildingDeleteView, RoomSaveView, RoomDeleteView, DormQueryByPageView, DormAssignView, DormExchangeView, DormCheckoutView, DormPublishSaveView, DormPublishQueryView, DormPublishDeleteView, DormAssignQueryView, BookQueryByPageView, BookSaveView, BookDeleteView, BorrowAddView, BorrowReturnView, BorrowQueryByPageView

urlpatterns = [
    path('building/queryByPage', BuildingQueryByPageView.as_view()),
    path('building/save', BuildingSaveView.as_view()),
    path('building/delete/<int:building_id>', BuildingDeleteView.as_view()),
    path('building/delete', BuildingDeleteView.as_view()),
    path('room/save', RoomSaveView.as_view()),
    path('room/delete/<int:room_id>', RoomDeleteView.as_view()),
    path('room/delete', RoomDeleteView.as_view()),
    path('dorm/queryByPage', DormQueryByPageView.as_view()),
    path('dorm/queryAssign', DormAssignQueryView.as_view()),
    path('dorm/assign', DormAssignView.as_view()),
    path('dorm/exchange', DormExchangeView.as_view()),
    path('dorm/checkout', DormCheckoutView.as_view()),
    path('dormPublish/save', DormPublishSaveView.as_view()),
    path('dormPublish/queryByPage', DormPublishQueryView.as_view()),
    path('dormPublish/delete/<int:publish_id>', DormPublishDeleteView.as_view()),
    path('dormPublish/delete', DormPublishDeleteView.as_view()),

    path('book/queryByPage', BookQueryByPageView.as_view()),
    path('book/save', BookSaveView.as_view()),
    path('book/delete/<int:book_id>', BookDeleteView.as_view()),
    path('book/delete', BookDeleteView.as_view()),
    path('borrow/add', BorrowAddView.as_view()),
    path('borrow/return/<str:borrow_id>', BorrowReturnView.as_view()),
    path('borrow/queryByPage', BorrowQueryByPageView.as_view()),
]
