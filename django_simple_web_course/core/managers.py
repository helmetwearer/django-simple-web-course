from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe

class StudentIdentificationDocumentManager(models.Manager):
    needs_implementaion = True

class StudentManager(models.Manager):
    def get_or_create_from_user(self, user=None):
        from .models import StudentIdentificationDocument
        if user is None:
            raise Exception("user option cannot be None in get_or_create_from_user")
        try:
            student = self.get(user=user)
        except TypeError:
            return None
        except self.model.DoesNotExist:
            student = self.create(user=user, email_address=user.email,
                first_name=user.first_name, last_name=user.last_name)
            for document in settings.IDENTIFICATION_DOCUMENTS:
                new_doc = StudentIdentificationDocument(student=student,
                    document_title=document.get('title', 'Title'),
                    document_description=document.get('description', 'Description'),
                    verification_required=document.get('verification_required', False),
                )
                new_doc.save()
            verified_doc_count = StudentIdentificationDocument.objects.filter(student=student,
                verification_required=True).count()
            if verified_doc_count == 0:
                print('no verification documents, auto verify')
                student.verified_on = timezone.now()
                student.verification_ready_on = timezone.now()
                student.save()

        return student


class CoursePageManager(models.Manager):

    def nav_page_split_for_course(self, course=None, page=None):

        if course is None and page is None:
            return ''
        if not page is None:
            page_to_use = page
            course_to_use = page.course
        else:
            course_to_use = course
        course_pages = course.course_pages.order_by('page_number')
        total_pages = course_pages.count()
        if  total_pages == 0:
            return ''
        guid_ordered_list = [ page.guid for page in course_pages]
        if page_to_use is None:
            page_to_use = course_pages[0]
        
        page_index = guid_ordered_list.index(page_to_use.guid)

        if total_pages <= 10:
            page_indexing_obj = set(range(1, total_pages + 1))
        else:
            page_indexing_obj = (set(range(1, 4))
                     | set(range(max(1, page_index - 1), min(page_index + 4, total_pages + 1)))
                     | set(range(total_pages - 2, total_pages + 1)))


        def display_at_index(index, guid_list, target_index):
            tag_url = reverse('course_page', kwargs={'page_guid':guid_list[index-1]})
            inner_tag = str(index) if index != target_index else '[ %s ]' % index
            return '<div class="col"><a href="%s">%s</a></div>' % (tag_url, inner_tag)

        # Display pages in order with ellipses
        def display():
            last_page = 0
            for p in sorted(page_indexing_obj):
                if p != last_page + 1: yield '<div class="col">...</div>'
                yield display_at_index(p, guid_ordered_list, page_index+1)
                last_page = p
        display_columns = ' '.join(display())
        return mark_safe('<div class="row page-navigation-bar">%s</div>' % display_columns)


