from typing import Any
from django.contrib.auth.models import User
from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from feed.models import Post
from followers.models import Follower
#I am adding
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .forms import ProfileImageForm  # assuming you've created this form
from .models import Profile 
# Create your views here.
class ProfileDetailView(DetailView):
    http_method_names = ["get"]
    template_name = "profiles/detail.html"
    model= User
    context_object_name = "user"
    slug_field= "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        self.request=request
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) :
        user = self.get_object()
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.filter(author=user).count()
        context['total_followers'] = Follower.objects.filter(following=user).count()
        context['total_following'] = Follower.objects.filter(followed_by=user).count()
        if self.request.user.is_authenticated:
            context['you_follow'] =  Follower.objects.filter(following=user, followed_by = self.request.user).exists()
        return context

# Add a new view for handling profile image upload/edit
class ProfileImageUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "profiles/editimage.html"
    form_class = ProfileImageForm
    success_url = "/"  # adjust the URL name as per your setup
    model = Profile

    def get_object(self, queryset=None):
        # Fetch the current user's profile
        return self.request.user.profile

class FollowView(LoginRequiredMixin, View) :
    http_method_names = ["post"]
    def post(self, request, *args, **kwargs):
        data = request.POST.dict()

        if "action" not in data or "username" not in data:
            return HttpResponseBadRequest("Missing data")
        
        try:
            other_user = User.objects.get(username=data['username'])

        except User.DoesNotExist:
            return HttpResponseBadRequest("Missing user")
        
        if data['action'] == "follow":
            #Follow 
            follower, created = Follower.objects.get_or_create(
                followed_by= request.user,
                following=other_user,
            )

        else:
            #unfollow
            try :
            #Follow 
                follower= Follower.objects.get(
                    followed_by= request.user,
                    following=other_user,
                )
            except Follower.DoesNotExist:
                follower = None

            if follower:
                follower.delete()
            
        return JsonResponse({
            'success' : True ,
            'wording' : "Unfollow" if data['action'] == "follow" else "Follow",
        })