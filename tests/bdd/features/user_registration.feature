Feature: Registro de usuarios buyer
  Como visitante del sistema
  Quiero poder registrarme
  Para usar la aplicación con rol de comprador (buyer)

  Scenario: Registro exitoso de un nuevo usuario buyer
    When me registro con email "nuevo_buyer@example.com" y password "SuperSecreto123!"
    Then el registro es exitoso
    And el usuario registrado tiene rol buyer
