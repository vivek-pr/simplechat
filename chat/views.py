from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth
from django.contrib.auth.models import User
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from chat.serializers import MessageSerializers
from chat.models import Message
from rest_framework import status
from django.db.models import Q

class Home(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'core/home.html'

    def get(self, request):
        queryset = User.objects.all().exclude(id=request.user.id)
        return Response({'users': queryset})

class Chat(APIView):
    """
    List all snippets, or create a new snippet.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'core/chat.html'

    def get(self, request, person_id, format=None):
        chat_partner = User.objects.get(id=person_id)
        snippets = Message.objects.filter(Q(sender=chat_partner, recipient=request.user) |
                                       Q(sender=request.user, recipient=chat_partner))
        serializer = MessageSerializers(snippets, many=True)
        return Response({'serializer':serializer.data, 'username':chat_partner})

    def post(self, request, person_id,  format=None):
        chat_partner = User.objects.get(id=person_id)

        try:
            message = Message.objects.create(sender=request.user, recipient=chat_partner, message=request.data['message'])
            serializer = MessageSerializers(message)
            return Response({'serializer':serializer.data, 'username':chat_partner}, status=status.HTTP_201_CREATED)
        except:
            return Response({'serializer':serializer.errors, 'username':chat_partner}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def settings(request):
    user = request.user

    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None

    try:
        twitter_login = user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'core/settings.html', {
        'github_login': github_login,
        'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })

@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'core/password.html', {'form': form})