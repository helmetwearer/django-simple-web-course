from django.db import models
from django.conf import settings
from django.utils import timezone

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


