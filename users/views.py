from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import LoginForm, StyledPasswordChangeForm


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember = form.cleaned_data.get('remember_me')
        if not remember:
            self.request.session.set_expiry(0)          # expires on browser close
        else:
            self.request.session.set_expiry(60 * 60 * 24 * 14)  # 2 weeks
        return super().form_valid(form)

    def form_invalid(self, form):
        # Distinguish wrong username vs wrong password for internal tool
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = form.data.get('username', '')
        if username and not User.objects.filter(username=username).exists():
            form.add_error('username', 'No account found with this username.')
        elif username:
            form.add_error('password', 'Incorrect password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)   # keeps session alive after pw change
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard')
    else:
        form = StyledPasswordChangeForm(request.user)
    return render(request, 'auth/change_password.html', {'form': form})
