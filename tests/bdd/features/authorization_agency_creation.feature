Feature: Restricciones de creación de usuarios agencia
  Como usuario no admin
  Quiero intentar crear un usuario agencia
  Para verificar que el sistema rechaza la operación

  Scenario: Buyer intenta crear un usuario agencia y recibe 403
    Given existe un usuario buyer logueado
    When intento crear un usuario agencia desde el endpoint protegido
    Then la respuesta HTTP es 403
