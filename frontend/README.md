# saas-frontend

React 19 + TypeScript SPA servida por Nginx (multi-stage Docker).

## Scripts

```bash
npm run dev        # Vite dev server (porta 5173)
npm run build      # tsc + Vite build → dist/
npm test           # Vitest
```

## Docker

```bash
docker build -t saas-frontend .
docker run -p 80:80 saas-frontend
```

Acessível em `https://app.{domain}` via Traefik.

O container usa usuário não-root `app` (UID 1001) e nginx customizado com `pid` e caches em `/tmp`.

## Stack

- React 19 · TypeScript 5.8 · Vite 6
- Vitest + Testing Library + jsdom
- Nginx stable-alpine


---

 ## Guia de Integração Frontend ↔ Backend

  1. Arquitetura de Comunicação
   * Base URL: https://<dominio>/api/v1
   * Protocolo: REST (JSON)
   * Camada de Borda: O frontend não fala diretamente com o backend. Ele passa pelo Traefik, que gerencia:
       * CORS: (Já configurado no Traefik para aceitar domínios autorizados).
       * Rate Limiting: (100 req/min por IP).
       * SSL/TLS: Terminação de HTTPS.

  2. Autenticação e Autorização (SSO)
  O sistema utiliza Forward Auth via oauth2-proxy + Keycloak.
   * Fluxo de Login: O frontend não deve implementar uma tela de login própria com usuário/senha. Se receber um 401 Unauthorized ou se não houver cookie de sessão, ele deve redirecionar o usuário para a URL de login do Proxy.
   * Headers de Identidade: O backend confia nos headers injetados pelo Proxy:
       * X-Auth-Request-User: ID do usuário.
       * X-Auth-Request-Email: Email do usuário.
   * Multi-tenancy (tenant_id): 
       * O tenant_id é extraído automaticamente do JWT pelo backend.
       * Dica para Desenvolvimento: O frontend pode enviar o header X-Tenant-ID manualmente para sobrescrever/testar tenants específicos se necessário.

  3. Endpoints Principais (API v1)

  ┌───────────┬────────┬─────────────────────────┬──────────────────────────────────────────────────────────────┐
  │ Recurso   │ Método │ Endpoint                │ Descrição                                                    │
  ├───────────┼────────┼─────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ Canais    │ GET    │ /channels/              │ Lista todos os canais conectados do tenant.                  │
  │           │ POST   │ /channels/              │ Cria um novo canal (WhatsApp, Telegram, etc).                │
  │           │ GET    │ /channels/{id}/qr       │ Obtém o QR Code (Base64) para canais de instância (Baileys). │
  │           │ POST   │ /channels/{id}/validate │ Força a re-validação do status do canal.                     │
  │ Mensagens │ GET    │ /messages/              │ Lista o histórico de mensagens (paginado).                   │
  │           │ POST   │ /messages/send          │ Envia uma nova mensagem (texto ou mídia).                    │
  │ Contatos  │ GET    │ /contacts/              │ Lista os contatos capturados pelos webhooks.                 │
  │ Saúde     │ GET    │ /health                 │ Check de status do backend.                                  │
  │ User Info │ GET    │ /me                     │ Retorna o perfil do usuário logado e suas permissões.        │
  └───────────┴────────┴─────────────────────────┴──────────────────────────────────────────────────────────────┘

  4. Requisitos de Dados (Frontend)
   * Formatos de Data: O backend envia e recebe datas no formato ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ).
   * Payload de Envio de Mensagem:

   1     {
   2       "channel_id": "uuid",
   3       "recipient": "+5511999999999",
   4       "content_type": "text",
   5       "text": "Mensagem aqui",
   6       "media_url": null
   7     }
   * Tratamento de Erros:
       * 400 Bad Request: Erro de validação de campo ou formato.
       * 401 Unauthorized: Sessão expirada ou inválida (Redirecionar para login).
       * 409 Conflict: Tentativa de criar recurso duplicado (ex: dois canais do mesmo tipo).
       * 429 Too Many Requests: Limite de taxa atingido.

  5. Checklist para o Frontend
   1. [ ] State Management: Não armazene o JWT no localStorage (o Proxy usa cookies HttpOnly).
   2. [ ] Interceptors: Configure um interceptor de resposta para capturar 401 e redirecionar para o login do Keycloak.
   3. [ ] Multi-tenant UI: A interface deve estar preparada para mostrar apenas dados do tenant_id atual (retornado pelo /me).
   4. [ ] Polling/Websockets: O backend atualiza o status das mensagens via Webhooks de terceiros. Para o dashboard ser "em tempo real", o frontend deve implementar polling ou aguardar a futura implementação de SSE/Websockets no backend.