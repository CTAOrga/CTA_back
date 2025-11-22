Feature: Autenticación a nivel servicio (controller)
  Para asegurar que el servicio valida credenciales correctamente

  Scenario: Password inválido
    Given existe un usuario buyer en la base
    When intento autenticar con password "wrong"
    Then la autenticación falla

  Scenario: Password válido
    Given existe un usuario buyer en la base
    When intento autenticar con password "secret"
    Then la autenticación es exitosa
