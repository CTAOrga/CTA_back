Feature: Restricciones de creación de usuarios agencia
  Como sistema
  Quiero controlar quién puede crear usuarios agencia
  Para garantizar que solo un Admin pueda hacerlo

  Scenario: Buyer intenta crear un usuario agencia y recibe 403
    Given existe un usuario buyer logueado
    When intento crear un usuario agencia desde el endpoint protegido
    Then la respuesta HTTP es 403

  Scenario: Admin crea un usuario agencia y recibe 201
    Given existe un usuario admin logueado
    When intento crear un usuario agencia desde el endpoint protegido como admin
    Then la respuesta HTTP es 201
    And la respuesta contiene un usuario agencia creado correctamente
