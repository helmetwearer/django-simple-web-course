from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from random import randrange

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
                student.verified_on = timezone.now()
                student.verification_ready_on = timezone.now()
                student.save()

        return student

class CourseTestManager(models.Manager):

    def create_answer_options_for_question_instance(self, question_instance):
        from .models import CourseTestQuestionAnswerOption

        question_obj = question_instance.course_test_question
        answer_length = question_obj.calculated_answer_length

        # no answers in the pool, can't create
        if answer_length <= 1:
            return None

        incorrect_answer_indexes_added = []
        order_keys_used = []
        # this structure exists to help random index placement
        answer_order_key = {i:None for i in range(0,answer_length)}
        correct_answer_placement_index = randrange(0, answer_length)
        order_keys_used.append(correct_answer_placement_index)
        answer_order_key[correct_answer_placement_index] = question_obj.correct_multiple_choice_answer
        
        wrong_answers = question_obj.other_multiple_choice_answers.order_by('-created')
        while len(incorrect_answer_indexes_added) < answer_length -1:
            # get an unused order key to place an answer
            random_order_key = randrange(0, answer_length)
            while random_order_key in order_keys_used:
                random_order_key = randrange(0, answer_length)
            order_keys_used.append(random_order_key)
            # get an unused wrong answer index
            wrong_answer_index = randrange(0, wrong_answers.count())
            while wrong_answer_index in incorrect_answer_indexes_added:
                 wrong_answer_index = randrange(0, wrong_answers.count())
            incorrect_answer_indexes_added.append(wrong_answer_index)
            # make structure assignment
            answer_order_key[random_order_key] = wrong_answers[wrong_answer_index]
        # now that we've filled the dict create a list comprehension
        # excluding none of the above and all the above answers
        print(answer_order_key)

        answer_list = [
            answer_order_key[key] for key in range(0,answer_length)
            if (not(answer_order_key[key].is_all_of_the_above) 
                and not(answer_order_key[key].is_none_of_the_above))
        ]
        # now we add a list only including none or all the aboves
        none_all_list = [
            answer_order_key[key] for key in range(0,answer_length)
            if (answer_order_key[key].is_all_of_the_above
                or answer_order_key[key].is_none_of_the_above)
        ]
        # we finally have all answers ordered, create the list
        final_list = answer_list + none_all_list
        for order, answer in enumerate(final_list):
            new_option = CourseTestQuestionAnswerOption.objects.create(
                question_instance=question_instance,
                answer_option=answer,
                order=order
            )
            new_option.save()

        return final_list


    def get_or_generate_test_instance(self, course_test, student, is_practice=False):
        from .models import CourseTestInstance, CourseTestQuestionInstance
        #look for an existing active test and return if relevant
        # we generate new practice tests after old ones are finished
        if is_practice:
            active_tests = course_test.course_test_instances.filter(student=student, 
                test_finished_on__isnull=True, is_practice=is_practice)
        # live test. Cannot have a retake marked, return completed tests as well
        # return of a completed test will mean inability to take a new one
        else:
            active_tests = course_test.course_test_instances.filter(student=student,
                is_practice=is_practice, retake__isnull=True)
        if active_tests.count() > 0:
            return active_tests[0]

        # no active tests found, generate one
        number_of_available_questions = course_test.number_of_available_questions
        # we can only generate if we have questions
        if number_of_available_questions > 0:
            new_test_instance = CourseTestInstance.objects.create(is_practice=is_practice,
                course_test=course_test, student=student)
            new_test_instance.save()
            # generate the questions
            
            available_questions = course_test.multiple_choice_test_questions.order_by('-created')
            indexes_added = []
            while len(indexes_added) < number_of_available_questions:
                random_index = randrange(0, number_of_available_questions)
                while random_index in indexes_added:
                    random_index = randrange(0, number_of_available_questions)
                indexes_added.append(random_index)
                random_question = available_questions[random_index]
                new_question = CourseTestQuestionInstance.objects.create(
                    course_test_instance=new_test_instance,
                    course_test_question=random_question,
                    order=len(indexes_added))
                new_question.save()
                self.create_answer_options_for_question_instance(new_question)

            return new_test_instance

        return None