from django.urls import path
from .views import (
    StudentQueryByIdCardView, StudentQueryByIdView, StudentAddView, StudentQueryByPageView, StudentFileAddView, StudentFileQueryView, StudentDeleteView, StudentArchiveView,
    CourseQueryByPageView, CourseSaveView, CourseDeleteView, CourseSelectableView,
    SchedulingSelectView, SchedulingAddView, SchedulingUpdateView, SchedulingDeleteView,
    EnrollmentAddView, EnrollmentCancelView, EnrollmentUpdateView, EnrollmentQueryByPageView, EnrollmentWorkNumView,
    ExamQueryByPageView, ExamAddView,
    ScoreAddView, ScoreImportView, ScoreQueryByPageView, ScoreRankView, ScoreDeleteView,
    AttendanceMarkView, AttendanceQueryView,
    ClassQueryByPageView, ClassSaveView, ClassDeleteView
)

urlpatterns = [
    path('student/queryByIdCard', StudentQueryByIdCardView.as_view()),
    path('student/queryById/<str:student_id>', StudentQueryByIdView.as_view()),
    path('student/add', StudentAddView.as_view()),
    path('student/queryByPage', StudentQueryByPageView.as_view()),
    path('student/delete/<str:student_id>', StudentDeleteView.as_view()),
    path('student/delete', StudentDeleteView.as_view()),
    path('student/archive', StudentArchiveView.as_view()),
    path('studentFile/add', StudentFileAddView.as_view()),
    path('studentFile/queryById/<str:stu_id>', StudentFileQueryView.as_view()),
    path('studentFile/queryByIdCard', StudentQueryByIdCardView.as_view()),

    path('course/queryByPage', CourseQueryByPageView.as_view()),
    path('course/save', CourseSaveView.as_view()),
    path('course/delete/<str:course_id>', CourseDeleteView.as_view()),
    path('course/delete', CourseDeleteView.as_view()),
    path('course/querySelectable', CourseSelectableView.as_view()),

    path('scheduling/selectWithConditions', SchedulingSelectView.as_view()),
    path('scheduling/add', SchedulingAddView.as_view()),
    path('scheduling/update', SchedulingUpdateView.as_view()),
    path('scheduling/delete/<int:id>', SchedulingDeleteView.as_view()),
    path('scheduling/delete', SchedulingDeleteView.as_view()),

    path('enrollment/add', EnrollmentAddView.as_view()),
    path('enrollment/cancel/<str:enroll_id>', EnrollmentCancelView.as_view()),
    path('enrollment/update', EnrollmentUpdateView.as_view()),
    path('enrollment/queryByPage', EnrollmentQueryByPageView.as_view()),
    path('enrollment/queryWorkNum', EnrollmentWorkNumView.as_view()),

    path('exam/queryByPage', ExamQueryByPageView.as_view()),
    path('examPaper/queryByPage', ExamQueryByPageView.as_view()),
    path('exam/add', ExamAddView.as_view()),

    path('score/add', ScoreAddView.as_view()),
    path('score/import', ScoreImportView.as_view()),
    path('score/queryByPage', ScoreQueryByPageView.as_view()),
    path('score/queryRank', ScoreRankView.as_view()),
    path('score/delete/<str:score_id>', ScoreDeleteView.as_view()),
    path('score/delete', ScoreDeleteView.as_view()),

    path('attendance/mark', AttendanceMarkView.as_view()),
    path('attendance/queryByPage', AttendanceQueryView.as_view()),

    path('class/queryByPage', ClassQueryByPageView.as_view()),
    path('class/save', ClassSaveView.as_view()),
    path('class/delete/<int:class_id>', ClassDeleteView.as_view()),
    path('class/delete', ClassDeleteView.as_view()),
]
