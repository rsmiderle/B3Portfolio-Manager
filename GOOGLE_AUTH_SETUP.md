# Configuração de Ambiente para Autenticação Google

Para configurar corretamente a autenticação Google OAuth no B3 Portfolio Manager, siga estas instruções:

## 1. Criar Credenciais no Google Cloud Platform

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Vá para "APIs e Serviços" > "Credenciais"
4. Clique em "Criar Credenciais" > "ID do Cliente OAuth"
5. Configure a tela de consentimento OAuth:
   - Tipo de usuário: Externo
   - Nome do aplicativo: B3 Portfolio Manager
   - Domínios autorizados: adicione seu domínio de produção
   - Escopos: email, profile
6. Crie um ID de cliente OAuth:
   - Tipo de aplicativo: Aplicativo da Web
   - Nome: B3 Portfolio Manager Web Client
   - URIs de redirecionamento autorizados: 
     - Para desenvolvimento local: `http://localhost:5000/auth/callback`
     - Para produção: `https://seu-dominio.com/auth/callback`
7. Anote o Client ID e Client Secret gerados

## 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
SECRET_KEY=chave_secreta_aleatoria_para_sessao
```

## 3. Testar o Fluxo de Autenticação

1. Inicie a aplicação com `python run.py`
2. Acesse a página inicial e clique em "Entrar com Google"
3. Você será redirecionado para a tela de login do Google
4. Após autenticação bem-sucedida, será redirecionado de volta para a aplicação

## 4. Verificação de Isolamento de Dados

Para verificar se o isolamento de dados está funcionando corretamente:

1. Faça login com uma conta Google
2. Crie algumas ações, relatórios e saldos
3. Faça logout
4. Faça login com outra conta Google
5. Verifique se os dados criados anteriormente não estão visíveis

## 5. Solução de Problemas

- **Erro de redirecionamento**: Verifique se a URI de redirecionamento está corretamente configurada no Google Cloud Console
- **Erro de autenticação**: Verifique se as variáveis de ambiente estão configuradas corretamente
- **Dados visíveis entre usuários**: Verifique se todas as consultas estão filtrando por `user_id`
