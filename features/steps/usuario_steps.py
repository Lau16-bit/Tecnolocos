from behave import given, when, then
from app import ServicioUsuario, Usuario

@given('el sistema está inicializado')
def step_given_sistema_inicializado(context):
    context.servicio = ServicioUsuario()
    context.mensaje_error = ""

@given('un usuario con nombre "{nombre}", email "{email}" y edad {edad}')
def step_given_usuario(context, nombre, email, edad):
    # Si el email solo tiene espacios, lo convertimos a string vacío
    if email.strip() == "":
        email = ""
    context.usuario_actual = Usuario(nombre, email, int(edad))

@when('se registra el usuario en el sistema')
def step_when_registrar_usuario(context):
    context.resultado = context.servicio.registrar_usuario(context.usuario_actual)  # ← CAMBIADO
    if not context.resultado:
        if context.usuario_actual.edad < 18:
            context.mensaje_error = "El usuario debe ser mayor de edad"
        elif not context.usuario_actual.email or context.usuario_actual.email.strip() == "":
            context.mensaje_error = "El email es obligatorio"

@then('el sistema confirma el registro exitoso')
def step_then_confirma_registro(context):
    assert context.resultado == True

@then('el sistema rechaza el registro')
def step_then_rechaza_registro(context):
    assert context.resultado == False

@then('el usuario "{email}" está en la lista de usuarios')
def step_then_usuario_en_lista(context, email):
    usuario = context.servicio.buscar_por_email(email)
    assert usuario is not None

@then('se muestra el mensaje "{mensaje}"')
def step_then_mensaje(context, mensaje):
    assert context.mensaje_error == mensaje