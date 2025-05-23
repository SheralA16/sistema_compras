from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .forms import UsuarioForm, UsuarioCreacionForm  # UsuarioCreationForm es tu versión personalizada de UserCreationForm
from apps.departamentos.models import Departamento
from .models import Usuario
from django.http import JsonResponse

User = get_user_model()

@login_required
@permission_required('usuarios.view_usuario', raise_exception=True)
def lista_usuarios(request):
    # Solo mostrar usuarios activos
    usuarios = User.objects.filter(is_active=True)
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
@permission_required('usuarios.view_usuario', raise_exception=True)
def lista_usuarios_inactivos(request):
    """Vista para ver solo usuarios inactivos"""
    usuarios = User.objects.filter(is_active=False).order_by('username')
    return render(request, 'usuarios/lista_inactivos.html', {'usuarios': usuarios})


@login_required
@permission_required('usuarios.add_usuario', raise_exception=True)
def crear_usuario(request):
    departamentos = Departamento.objects.all()  # Traemos todos los departamentos

    if request.method == 'POST':
        form = UsuarioCreacionForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            # Asignar departamento si se envió y es válido
            departamento_id = request.POST.get('departamento')
            if departamento_id:
                try:
                    departamento = departamentos.get(id=departamento_id)
                    usuario.departamento = departamento
                except Departamento.DoesNotExist:
                    usuario.departamento = None

            usuario.save()
            # Importante: guardar M2M para los grupos
            form.save_m2m()

            messages.success(request, 'Usuario creado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioCreacionForm()

    return render(request, 'usuarios/formulario.html', {
        'form': form,
        'departamentos': departamentos,
    })

@login_required
@permission_required('usuarios.change_usuario', raise_exception=True)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, pk=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            # Guardamos el usuario, commit=True para que guarde y actualice grupos
            form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
@permission_required('usuarios.delete_usuario', raise_exception=True)
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, pk=usuario_id)
    if request.method == 'POST':
        # En lugar de eliminar, cambiar el estado is_active
        if usuario.is_active:
            usuario.is_active = False
            messages.success(request, f'Usuario {usuario.username} desactivado correctamente.')
        else:
            usuario.is_active = True
            messages.success(request, f'Usuario {usuario.username} activado correctamente.')
        
        usuario.save()
        return redirect('lista_usuarios')
    
    return render(request, 'usuarios/confirmar_eliminacion.html', {'usuario': usuario})

@login_required
def obtener_departamento_por_solicitante(request, usuario_id):
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
        if usuario.departamento:
            return JsonResponse({'departamento_id': usuario.departamento.id, 'departamento_nombre': usuario.departamento.nombre})
        else:
            return JsonResponse({'departamento_id': None, 'departamento_nombre': 'No asignado'})
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)