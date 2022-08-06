import datetime

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView

from .services import make_request_get_clicks


class LoginView(TemplateView):
    template_name = 'core/login.html'

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse_lazy('main'))
            else:
                return HttpResponse("Inactive user.")

        return render(request, "core/login.html")


class MainView(TemplateView):
    template_name = 'core/main.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        user = self.request.user.username
        date_today = datetime.date.today().strftime('%Y-%m-%d')
        context['from_date'] = date_today

        clicks = make_request_get_clicks(from_date=date_today,
                                         user=user)
        context['clicks'] = clicks

        return context

    def post(self, request):
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        user = request.user.username

        clicks = make_request_get_clicks(
            from_date=from_date,
            to_date=to_date,
            user=user
        )

        context = {
            'from_date': from_date,
            'to_date': to_date,
            'clicks': clicks
        }

        return render(request=request,
                      template_name=self.template_name,
                      context=context)
