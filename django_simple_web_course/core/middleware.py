from django.utils import timezone
from .models import CoursePageViewInstance, Student, CourseTestInstance
from django.http import HttpResponseRedirect

class PageViewInstanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if a page view is found on the session it was made from a previous request
        page_view_instance_guid = request.session.pop('page_view_instance_guid', None)
        if page_view_instance_guid:
            try:
                page_view_instance = CoursePageViewInstance.objects.get(guid=page_view_instance_guid)
            except CoursePageViewInstance.DoesNotExist:
                page_view_instance = None
                print('page view instance with guid %s does not exist' % page_view_instance_guid)
            # we've detected a previous instance, mark it finished, calculate time credit
            if page_view_instance:
                page_view_instance.page_view_stop = timezone.now()
                maximum_idle_time_seconds = page_view_instance.course_view_instance.course.maximum_idle_time_seconds
                seconds_diff = (page_view_instance.page_view_stop - page_view_instance.page_view_start).seconds
                if seconds_diff > maximum_idle_time_seconds:
                    seconds_diff = maximum_idle_time_seconds
                page_view_instance.total_seconds_spent = seconds_diff
                page_view_instance.save()


        response = self.get_response(request)

        return response

class LiveTestRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if the guid is missing from the session, rather than set to None, initialize
        if 'live_test_guid' not in request.session and not request.user.is_anonymous:
            request.session['live_test_guid'] = None
            try:
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                student = None
            potential_live_tests = CourseTestInstance.objects.filter(is_practice=False,
                student=student, test_started_on__isnull=False, 
                test_finished_on__isnull=True,
            )
            
            for test in potential_live_tests:
                if not test.is_complete:
                    request.session['live_test_guid'] = str(test.guid)
           
        if 'live_test_guid' in request.session and request.session['live_test_guid']:
            test = CourseTestInstance.objects.get(guid=request.session['live_test_guid'])
            # if the test is finished remove from session
            if test.is_complete:
                removed_guid = request.session.pop('live_test_guid')
            # test isn't done and you are not where you are supposed to be, redirect to test home
            elif not request.path in test.live_test_allowed_urls:
                return HttpResponseRedirect(test.home_url)

        response = self.get_response(request)

        return response