# 📋 Documentação - Seletor de Perfis

## ✨ O que foi implementado?

Adicionamos um **seletor de perfis interativo** na barra superior (navbar) da aplicação que permite alternar entre os 3 tipos de usuários:

- **⚙️ Administrador** (Cinza): Central de despacho
- **🔍 Cliente** (Azul): Rastreamento público
- **🚚 Entregador** (Amarelo): Gerenciamento de rotas

## 🎯 Características

### 1. **Seletor de Perfis Visual**
- Navbar no topo da página com 3 botões
- Botão do perfil ativo é destacado com cor específica
- Fácil alternância com um clique

### 2. **Persistência de Dados**
- **localStorage** salva automaticamente:
  - O perfil ativo (para quando você recarregar a página)
  - Dados de cada formulário separadamente por perfil
  - Cada perfil tem seu próprio espaço de armazenamento

### 3. **Preservação de Informações**
- Ao trocar de perfil, os dados NÃO são perdidos
- Se você preencher algo no perfil Admin e trocar para Cliente, quando voltar para Admin seus dados estarão lá
- Cada formulário mantém suas informações independentemente

### 4. **Responsividade**
- Funciona em desktop, tablet e mobile
- Botões se reorganizam em telas pequenas

## 🚀 Como Usar

### Alternando entre Perfis

1. Abra `index.html` no navegador
2. Veja a navbar no topo com os 3 botões de perfil
3. Clique em qualquer botão para trocar de perfil
4. O botão do perfil ativo fica colorido

### Exemplo de Demonstração

```
1. Clique em "⚙️ Administrador"
   → Preencha um código de rastreio na seção Admin
   
2. Clique em "🔍 Cliente"
   → Veja o código vazio (dados separados)
   → Preencha um código diferente para Cliente
   
3. Volte para "⚙️ Administrador"
   → Seu primeiro código está ainda lá! ✅
   
4. Recarregue a página (F5)
   → O sistema remembrou qual era seu último perfil
   → Os dados foram preservados
```

## 🛠️ Detalhes Técnicos

### Arquivos Modificados

#### **frontend/index.html**
- Adicionado `<nav class="profile-navbar">` no topo
- 3 botões com `data-profile="admin|cliente|entregador"`
- Cada botão chama `trocarPerfil(perfilId)`

#### **frontend/style.css**
- Estilos para `.profile-navbar` (navbar superior)
- Estilos para `.profile-btn` (botões)
- Cores específicas por perfil:
  - Admin: `#6c757d` (cinza)
  - Cliente: `#007bff` (azul)
  - Entregador: `#ffc107` (amarelo)
- Design responsivo com `@media (max-width: 600px)`

#### **frontend/script.js**
Novas funções adicionadas:

```javascript
// Inicializa o perfil ao carregar
document.addEventListener('DOMContentLoaded', function() {
    const perfilSalvo = localStorage.getItem('perfilAtivo') || 'cliente';
    trocarPerfil(perfilSalvo, true);
});

// Troca de perfil com salvamento automático
function trocarPerfil(novoPerfil, inicializando = false)

// Salva dados do formulário do perfil atual
function salvarDadosPerfil()

// Restaura dados salvos do perfil
function restaurarDadosPerfil(perfil)
```

Além disso, todas as funções de API foram atualizadas para chamar `salvarDadosPerfil()` após sucesso:
- `cadastrarEncomenda()`
- `atribuirEntregador()`
- `rastrearEncomenda()`
- `carregarPainel()`
- `atualizarStatus()`

### localStorage - Estrutura

```javascript
localStorage.getItem('perfilAtivo')      // "admin" | "cliente" | "entregador"
localStorage.getItem('dados_admin')      // JSON com dados do Admin
localStorage.getItem('dados_cliente')    // JSON com dados do Cliente
localStorage.getItem('dados_entregador') // JSON com dados do Entregador
```

## 🧪 Testando a Funcionalidade

### Teste Manual

1. Abra `test-profiles.html` no navegador
2. Clique em "▶️ Executar Todos os Testes"
3. Veja os resultados dos 5 testes de validação

### Teste Prático

1. Abra `index.html`
2. Perfil padrão: **Cliente**
3. Preencha um campo (ex: código de rastreio)
4. Clique no botão **Administrador**
5. Veja que o campo está vazio (dados do Admin)
6. Volte ao **Cliente**
7. Seu código deve estar lá! ✅

### Teste de Persistência

1. Preencha dados em cada perfil
2. Recarregue a página (F5 ou Ctrl+R)
3. O sistema deve lembrar qual era seu último perfil
4. Todos os dados devem estar preservados

## 📊 Estrutura Visual

```
┌─────────────────────────────────────────┐
│ Selecione seu Perfil:                   │
│ [⚙️ Admin] [🔍 Cliente] [🚚 Entregador] │ ← Navbar Nova
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ 📦 Sistema de Logística Integrada       │ ← Header Existente
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ ⚙️ Central de Despacho (Admin)          │
│ [Inputs...] [Botões...]                 │
├─────────────────────────────────────────┤
│ 🔍 Rastreio Público (Cliente)           │
│ [Inputs...] [Botões...]                 │
├─────────────────────────────────────────┤
│ 🚚 Painel do Entregador                 │
│ [Inputs...] [Botões...]                 │
└─────────────────────────────────────────┘
```

## ⚡ Benefícios

✅ **Para Demonstrações**: Alterne facilmente entre perfis sem perder dados
✅ **Para Desenvolvimento**: localStorage não precisa de backend adicional
✅ **Para UX**: Interface clara e intuitiva
✅ **Para Mobile**: Design responsivo funciona em qualquer dispositivo
✅ **Para Persistência**: Dados não são perdidos ao recarregar

## 🔍 Como o localStorage Funciona

O localStorage é um mecanismo do navegador que persiste dados localmente:

```javascript
// Salvar
localStorage.setItem('chave', 'valor');

// Recuperar
localStorage.getItem('chave'); // 'valor'

// Limpar
localStorage.removeItem('chave');
localStorage.clear(); // Remove tudo
```

Os dados permanecem mesmo após:
- ✅ Fechar e reabrir o navegador
- ✅ Recarregar a página
- ✅ Alternar entre abas

Os dados são perdidos quando:
- ❌ Limpar o cache/cookies do navegador
- ❌ Usar modo privado/anônimo (em alguns navegadores)

## 🚀 Próximas Melhorias Possíveis

1. Adicionar ícone de perfil com foto do usuário
2. Salvar histórico de operações por perfil
3. Tema escuro adaptado por perfil
4. Adicionar novos perfis (Supervisor, etc.)
5. Sincronizar perfis entre dispositivos com backend

## 📝 Notas

- O sistema ainda usa localStorage do navegador (cliente-side)
- Para uma solução mais robusta, considere salvar no backend
- Cada navegador/computador terá seu próprio localStorage
- O localStorage tem limite de ~5-10MB por domínio

---

**Data de Implementação**: 2026-06-01
**Versão**: 1.0
**Status**: ✅ Pronto para uso
