Feature: Autenticación a nivel servicio (controller)
  Para asegurar que el servicio valida credenciales correctamente

  Scenario: Password inválido
    Given existe un usuario buyer en la base
    When intento autenticar con password "wrong"
    Then la autenticación falla

  Scenario: Password válido (buyer)
    Given existe un usuario buyer en la base
    When intento autenticar con password "secret"
    Then la autenticación es exitosa

  Scenario: Password inválido para admin
    Given existe un usuario admin en la base
    When intento autenticar el admin con password "wrong"
    Then la autenticación falla

  Scenario: Password válido (admin)
    Given existe un usuario admin en la base
    When intento autenticar el admin con password "secret"
    Then la autenticación es exitosa como admin
