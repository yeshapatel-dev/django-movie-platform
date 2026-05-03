from urllib import request
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin # type: ignore
from django.shortcuts import redirect, render, get_object_or_404 # type: ignore
from django.contrib import messages # type: ignore
from .models import Review

class AdminRequiredMixin(UserPassesTestMixin):
    """Only allow admin role."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_role == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('movies:home')
      

class UserAccessMixin(LoginRequiredMixin):
    """Allow only logged-in regular users to add reviews."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_role == 'user'

    def handle_no_permission(self):
        return redirect('movies:signin')

class ReviewAuthorMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        review_id = self.kwargs.get('review_id')
        if review_id:
            review = get_object_or_404(Review, id=review_id)
            return review.user_name == self.request.user
        # If adding a new review (no review_id), just ensure user is logged in (LoginRequiredMixin handles this)
        return True