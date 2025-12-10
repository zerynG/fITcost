from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Поиск пользователя по email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'})

        # Аутентификация
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/home/'})
        else:
            return JsonResponse({'success': False, 'message': 'Неверный пароль'})

    return render(request, 'login/login.html')  # Путь к шаблону



def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Проверка паролей
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Пароли не совпадают'})

        # Проверка существования пользователя
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с таким email уже существует'})

        # Создание пользователя
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            user.save()

            # Автоматический вход после регистрации
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/home/'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка при создании пользователя: {str(e)}'})

    return render(request, 'login/login.html')  # Используем тот же шаблон


def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login:auth')
    
    # Получаем информацию о пользователе
    user = request.user
    
    # Получаем полное имя из профиля
    full_name_parts = []
    if user.last_name:
        full_name_parts.append(user.last_name)
    if user.first_name:
        full_name_parts.append(user.first_name)
    
    # Пытаемся получить отчество из профиля
    try:
        profile = user.profile
        if profile and profile.patronymic:
            full_name_parts.append(profile.patronymic)
    except AttributeError:
        # Профиль не существует, пропускаем отчество
        pass
    
    # Формируем полное имя
    full_name = ' '.join(full_name_parts) if full_name_parts else user.get_full_name() or user.username
    
    # Определяем роль/права доступа
    user_roles = []
    
    # Проверяем, является ли пользователь суперпользователем
    if user.is_superuser:
        user_roles.append('Глобальный администратор')
    elif user.is_staff:
        user_roles.append('Персонал')
    
    # Получаем группы пользователя
    groups = user.groups.all()
    if groups.exists():
        group_names = [group.name for group in groups]
        user_roles.extend(group_names)
    
    # Если нет ролей, показываем стандартное сообщение
    if not user_roles:
        user_roles.append('Пользователь')
    
    # Объединяем роли в строку
    role_display = ', '.join(user_roles)
    
    context = {
        'user_full_name': full_name,
        'user_role': role_display,
        'user_profile': getattr(user, 'profile', None),
    }
    
    return render(request, 'login/home.html', context)


def logout_view(request):
    logout(request)
    return redirect('login:auth')