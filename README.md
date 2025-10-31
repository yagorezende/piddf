# PIDDF - Plataforma de Identidade Digital Descentralizada com Autenticação Federada

## Sobre o Projeto

O PIDDF (Plataforma de Identidade Digital Descentralizada com Autenticação Federada) é uma solução completa para gerenciamento de identidades digitais descentralizadas (DIDs) e credenciais verificáveis (VCs). O projeto implementa uma arquitetura moderna e segura baseada em padrões W3C para DIDs e VCs, integrando múltiplos componentes através de Docker Compose.

## Arquitetura

O projeto é composto por quatro componentes principais que trabalham de forma integrada:

### 1. PIDDF-VCS (Verifiable Credential Service)

Módulo desenvolvido especificamente pelo PIDDF para realizar a emissão e verificação de Credenciais Verificáveis (VCs). Este componente:

- Emite credenciais verificáveis seguindo os padrões W3C
- Verifica credenciais utilizando DIDs (Decentralized Identifiers)
- Integra-se com o OpenBao para assinatura criptográfica das credenciais
- Fornece APIs para gerenciamento do ciclo de vida das credenciais

### 2. OpenBao

Sistema de gerenciamento de segredos e chaves criptográficas. O OpenBao é responsável por:

- Armazenar e gerenciar chaves privadas de forma segura
- Fornecer serviços de assinatura para o PIDDF-VCS
- Garantir a integridade criptográfica das credenciais emitidas
- Implementar políticas de acesso e controle de segredos

### 3. Trustbloc Orb

Plataforma para gerenciamento de DIDs (Decentralized Identifiers). O Trustbloc Orb:

- Gerencia o registro e resolução de DIDs
- Mantém um ledger distribuído de operações DID
- Suporta múltiplos métodos DID
- Permite a verificação independente de identidades descentralizadas

### 4. Keycloak

Servidor de autenticação e autorização baseado em OIDC (OpenID Connect). O Keycloak fornece:

- Autenticação federada de usuários
- Single Sign-On (SSO)
- Gerenciamento de identidades e acessos
- Integração com protocolos OIDC e SAML

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- [Docker](https://docs.docker.com/get-docker/) (versão 20.10 ou superior)
- [Docker Compose](https://docs.docker.com/compose/install/) (versão 2.0 ou superior)
- Git

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/yagorezende/piddf.git
cd piddf
```

2. Configure as variáveis de ambiente (se necessário):

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Inicie os serviços com Docker Compose:

```bash
docker-compose up -d
```

4. Verifique se todos os serviços estão rodando:

```bash
docker-compose ps
```

## Configuração

### Configuração Inicial

Após iniciar os serviços, é necessário realizar algumas configurações iniciais:

1. **Keycloak**: Acesse `http://localhost:8080` para configurar realms e clientes OIDC
2. **OpenBao**: Inicialize e unseal o vault conforme documentação do OpenBao
3. **Trustbloc Orb**: Configure os endpoints e parâmetros de rede
4. **PIDDF-VCS**: Configure a integração com os demais componentes

### Variáveis de Ambiente

As principais variáveis de ambiente incluem:

- `KEYCLOAK_ADMIN`: Usuário administrador do Keycloak
- `KEYCLOAK_ADMIN_PASSWORD`: Senha do administrador
- `OPENBAO_ADDR`: Endereço do servidor OpenBao
- `ORB_HOST`: Host do servidor Trustbloc Orb
- Outras configurações específicas de cada componente

## Uso

### Emitindo uma Credencial Verificável

```bash
# Exemplo de requisição para emitir uma VC
curl -X POST http://localhost:8081/api/v1/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "holder": "did:example:123",
    "claims": {
      "name": "João Silva",
      "email": "joao@example.com"
    }
  }'
```

### Verificando uma Credencial

```bash
# Exemplo de requisição para verificar uma VC
curl -X POST http://localhost:8081/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "credential": "<VC_JWT_TOKEN>"
  }'
```

### Criando um DID

```bash
# Exemplo de criação de DID através do Trustbloc Orb
curl -X POST http://localhost:48326/sidetree/v1/operations \
  -H "Content-Type: application/json" \
  -d '{
    "type": "create",
    "suffixData": {...},
    "delta": {...}
  }'
```

## Estrutura do Projeto

```
piddf/
├── docker-compose.yml       # Orquestração dos serviços
├── .env.example            # Exemplo de variáveis de ambiente
├── piddf-vcs/              # Código do módulo PIDDF-VCS
├── configs/                # Configurações dos serviços
│   ├── keycloak/          # Configurações do Keycloak
│   ├── openbao/           # Configurações do OpenBao
│   └── orb/               # Configurações do Trustbloc Orb
└── docs/                   # Documentação adicional
```

## Desenvolvimento

### Executando em Modo de Desenvolvimento

```bash
docker-compose -f docker-compose.dev.yml up
```

### Logs

Para visualizar os logs de um serviço específico:

```bash
docker-compose logs -f <nome-do-serviço>
```

### Parando os Serviços

```bash
docker-compose down
```

Para remover também os volumes:

```bash
docker-compose down -v
```

## Tecnologias Utilizadas

- **DIDs**: Decentralized Identifiers (W3C Standard)
- **VCs**: Verifiable Credentials (W3C Standard)
- **OIDC**: OpenID Connect
- **Docker**: Containerização
- **OpenBao**: Gerenciamento de segredos
- **Trustbloc Orb**: DID Management
- **Keycloak**: Identity and Access Management

## Segurança

⚠️ **Importante**: 

- Nunca exponha as portas dos serviços diretamente na internet sem configuração adequada de segurança
- Altere todas as senhas padrão antes de usar em produção
- Configure TLS/SSL para comunicação entre serviços em ambiente de produção
- Mantenha os componentes atualizados com as últimas versões de segurança

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença [especificar licença].

## Contato

Yago Rezende - yagorezende@id.uff.br

Link do Projeto: [https://github.com/yagorezende/piddf](https://github.com/yagorezende/piddf)

## Referências

- [W3C DID Specification](https://www.w3.org/TR/did-core/)
- [W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model/)
- [OpenBao Documentation](https://openbao.org/)
- [Trustbloc Orb](https://github.com/trustbloc/orb)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
