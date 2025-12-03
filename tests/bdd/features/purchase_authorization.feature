Feature: Restricciones de compra de autos
  Como sistema
  Quiero controlar quién puede crear compras
  Para garantizar que solo un Buyer pueda comprar autos

  Scenario: Buyer realiza una compra y recibe 201
    Given existe un usuario buyer logueado
    And existe una listing disponible
    When intento crear una compra para esa listing
    Then la respuesta HTTP es 201
    And la respuesta contiene una compra creada correctamente
