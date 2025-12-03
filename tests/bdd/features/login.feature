Feature: Autenticación vía API HTTP
  Como sistema
  Quiero permitir que usuarios se logueen
  Para que obtengan un token de acceso

  Scenario: Buyer se loguea con credenciales válidas
    Given existe un usuario buyer en la base
    When hago login con email "buyer@example.com" y password "secret"
    Then la autenticación HTTP es exitosa
    And la respuesta incluye un access token

  Scenario: Admin se loguea con credenciales válidas
    Given existe un usuario admin en la base
    When hago login con email "admin@example.com" y password "secret"
    Then la autenticación HTTP es exitosa
    And la respuesta incluye un access token

  Scenario: Login con password incorrecto
    Given existe un usuario buyer en la base
    When hago login con email "buyer@example.com" y password "wrong"
    Then la autenticación HTTP falla
