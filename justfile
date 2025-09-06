# alias para el comando principal de docker-compose
COMPOSE_COMMAND := "docker-compose -f ./devops/compose.yml"

# Levanta los servicios de Docker en segundo plano (-d)
up:
    {{COMPOSE_COMMAND}} up -d

# Detiene y elimina los contenedores, redes y volúmenes
down:
    {{COMPOSE_COMMAND}} down

# Buildea la imagen 
build:
    {{COMPOSE_COMMAND}} build

# Ejecuta un comando dentro de un servicio (por defecto, una terminal bash en el servicio 'app')
exec service='backend' command='bash':
    {{COMPOSE_COMMAND}} exec {{service}} {{command}}


