Feature: Gestión de Usuarios
Como administrador del sistema
Quiero gestionar el registro de usuarios
Para mantener el control de acceso

Background:
Given el sistema está inicializado

Scenario: Registrar un usuario mayor de edad exitosamente
Given un usuario con nombre "Carlos Gomez", email "carlos@mail.com" y edad 30
When se registra el usuario en el sistema
Then el sistema confirma el registro exitoso
And el usuario "carlos@mail.com" está en la lista de usuarios

Scenario: Intentar registrar un usuario menor de edad
Given un usuario con nombre "Luis", email "luis@mail.com" y edad 16
When se registra el usuario en el sistema
Then el sistema rechaza el registro
And se muestra el mensaje "El usuario debe ser mayor de edad"

Scenario: Intentar registrar un usuario con email vacío
  Given un usuario con nombre "Maria", email "  " y edad 25
  When se registra el usuario en el sistema
  Then el sistema rechaza el registro
  And se muestra el mensaje "El email es obligatorio"