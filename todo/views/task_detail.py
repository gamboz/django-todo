import datetime
import os

import bleach
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from todo.defaults import defaults
from todo.features import HAS_TASK_MERGE
from todo.forms import AddEditTaskForm, AddEditCommentForm, AttachmentFormSet
from todo.models import Attachment, Comment, Task
from todo.utils import (
    send_email_to_thread_participants,
    staff_check,
    toggle_task_completed,
    user_can_read_task,
)

if HAS_TASK_MERGE:
    from dal import autocomplete


# def handle_file_uploads(request, task, comment):
#     """Upload files."""
#     # Handle uploaded files
#     if request.FILES.get("attachment_file_input"):
#         file = request.FILES.get("attachment_file_input")

#         if file.size > defaults("TODO_MAXIMUM_ATTACHMENT_SIZE"):
#             messages.error(
#                 request,
#                 "File exceeds maximum attachment size"
#                 f" {defaults('TODO_MAXIMUM_ATTACHMENT_SIZE')}.")
#             return redirect("todo:task_detail", task_id=task.id)

#         name, extension = os.path.splitext(file.name)

#         if extension not in defaults("TODO_LIMIT_FILE_ATTACHMENTS"):
#             messages.error(
#                 request,
#                 f"This site does not allow upload of {extension} files.")
#             return redirect("todo:task_detail", task_id=task.id)

#         Attachment.objects.create(
#             comment=comment,
#             file=file
#         )
#         messages.success(request, "File attached successfully")


def handle_add_comment(request, task, comment_form, attachments_formset):
    """Add a comment and its attachments and notify."""
    if not request.POST.get("add_comment"):
        return (comment_form, attachments_formset)

    comment_form = AddEditCommentForm(
        request.POST, request.FILES,
        # instance=task  # NO: CommentForm ↔ Comment obj!
    )

    # import ipdb; ipdb.set_trace()
    if comment_form.is_valid():
        # TODO: with transaction...
        comment = comment_form.save(commit=False)
        comment.task = task
        # TODO: check if `bleach.clean()` messes up XML input for `<x/>` tags
        # comment.body = bleach.clean(comment_form.cleaned_data["body"], strip=True)
        comment.author = request.user

        attachments_formset = AttachmentFormSet(
            request.POST, request.FILES,  # comment_id=comment
        )
        if attachments_formset.is_valid():
            comment.save()
            attachments = attachments_formset.save(commit=False)
            for attachment in attachments:
                attachment.comment_id = comment.id
                attachment.save()

            send_email_to_thread_participants(
                task,
                comment.body,
                request.user,
                subject='New comment posted on task "{}"'.format(task.title),
            )

            messages.success(
                request,
                "Comment posted. Notification email sent to thread participants.")

            # If all went well, reset the forms, so that they don't
            # bring unwanted info back to the task_detail page.
            #
            # However, do not just ignore them from our caller,
            # because they are needed in case of validation problems.
            comment_form = AddEditCommentForm()
            attachments_formset = AttachmentFormSet()

    return (comment_form, attachments_formset)


@login_required
@user_passes_test(staff_check)
def task_detail(request, task_id: int) -> HttpResponse:
    """View task details.

    Allow task details to be edited. Process new comments on task.
    """
    # import ipdb; ipdb.set_trace()
    task = get_object_or_404(Task, pk=task_id)
    comment_list = Comment.objects.filter(task=task_id).order_by("-date")

    # Ensure user has permission to view task. Superusers can view all tasks.
    # Get the group this task belongs to, and check whether current
    # user is a member of that group.
    if not user_can_read_task(task, request.user):
        raise PermissionDenied

    # Handle task merging
    if not HAS_TASK_MERGE:
        merge_form = None
    else:

        class MergeForm(forms.Form):
            merge_target = forms.ModelChoiceField(
                queryset=Task.objects.all(),
                widget=autocomplete.ModelSelect2(
                    url=reverse("todo:task_autocomplete",
                                kwargs={"task_id": task_id})
                ),
            )

        # Handle task merging
        if not request.POST.get("merge_task_into"):
            merge_form = MergeForm()
        else:
            merge_form = MergeForm(request.POST)
            if merge_form.is_valid():
                merge_target = merge_form.cleaned_data["merge_target"]
            if not user_can_read_task(merge_target, request.user):
                raise PermissionDenied

            task.merge_into(merge_target)
            return redirect(reverse("todo:task_detail",
                                    kwargs={"task_id": merge_target.pk}))

    # Save submitted comments
    # Handling comments and attachments before or after handling the
    # task itself is indifferent, because, as long as the reference to
    # the task does not change, then one can modify the two
    # separately.
    comment_form = AddEditCommentForm()
    attachments_formset = AttachmentFormSet()
    (comment_form, attachments_formset) = handle_add_comment(
        request, task, comment_form, attachments_formset)

    # Save task edits
    if not request.POST.get("add_edit_task"):
        form = AddEditTaskForm(request.user, instance=task,
                               initial={"task_list": task.task_list})
    else:
        form = AddEditTaskForm(
            request.user, request.POST, instance=task,
            initial={"task_list": task.task_list}
        )

        if form.is_valid():
            item = form.save(commit=False)
            # item.note = bleach.clean(form.cleaned_data["note"], strip=True)
            item.title = bleach.clean(form.cleaned_data["title"], strip=True)
            item.save()
            messages.success(request, "The task has been edited.")
            return redirect(
                "todo:list_detail",
                list_id=task.task_list.id, list_slug=task.task_list.slug
            )

    # Mark complete
    if request.POST.get("toggle_done"):
        results_changed = toggle_task_completed(task.id)
        if results_changed:
            messages.success(request,
                             f"Changed completion status for task {task.id}")

        return redirect("todo:task_detail", task_id=task.id)

    if task.due_date:
        thedate = task.due_date
    else:
        thedate = datetime.datetime.now()

    context = {
        "task": task,
        "comment_list": comment_list,
        "form": form,
        "merge_form": merge_form,
        "comment_form": comment_form,
        "attachments_formset": attachments_formset,
        "thedate": thedate,
        "comment_classes": defaults("TODO_COMMENT_CLASSES"),
        "attachments_enabled": defaults("TODO_ALLOW_FILE_ATTACHMENTS"),
    }

    return render(request, "todo/task_detail.html", context)
