from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import AudioFile, AnalysisResult
from .utils import analyze_speech
from django.urls import reverse_lazy

class DashboardView(LoginRequiredMixin, ListView):
    model = AnalysisResult
    template_name = 'analysis/dashboard.html'
    context_object_name = 'results'
    ordering = ['-created_at']

    def get_queryset(self):
        return AnalysisResult.objects.filter(audio_file__user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = self.get_queryset()
        if results.exists():
            context['avg_wpm'] = sum(r.wpm for r in results) / results.count()
            context['total_fillers'] = sum(r.total_fillers for r in results)
        else:
            context['avg_wpm'] = 0
            context['total_fillers'] = 0
        return context

@login_required
def upload_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        title = request.POST.get('title', 'Untitled Analysis')
        
        if audio_file:
            # Save audio file
            obj = AudioFile.objects.create(file=audio_file, title=title, user=request.user)
            
            # Run analysis
            analysis_data = analyze_speech(obj.file.path)
            
            # Save results
            AnalysisResult.objects.create(
                audio_file=obj,
                **analysis_data
            )
            
            return redirect('dashboard')
            
    return render(request, 'analysis/upload.html')

class ResultDetailView(LoginRequiredMixin, DetailView):
    model = AnalysisResult
    template_name = 'analysis/result_detail.html'
    context_object_name = 'result'

    def get_queryset(self):
        return AnalysisResult.objects.filter(audio_file__user=self.request.user)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'analysis/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'analysis/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
