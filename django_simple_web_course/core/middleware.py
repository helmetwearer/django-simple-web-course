from django.utils import timezone
from .models import CoursePageViewInstance

class PageViewInstanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

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