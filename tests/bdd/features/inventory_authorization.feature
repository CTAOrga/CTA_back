Feature: Restricciones de acceso al inventario
  Como sistema
  Quiero controlar quién puede crear items de inventario
  Para garantizar que solo una Agency pueda hacerlo

  Scenario: Buyer intenta crear un item de inventario y recibe 403
    Given existe un usuario buyer logueado
    When intento crear un item de inventario
    Then la respuesta HTTP es 403

  Scenario: Agency crea un item de inventario y recibe 201
    Given existe un usuario agency logueado
    And existe un CarModel "Fiat" "Cronos" en el catálogo
    When intento crear un item de inventario como agency
    Then la respuesta HTTP es 201
    And la respuesta contiene un item de inventario creado correctamente

