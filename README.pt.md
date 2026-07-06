# [Machine Portal](https://jorges15.github.io/MachinePortal/)

[English](README.md) · **Português**

**Painel de acesso remoto para o seu chão de fábrica.**
O Machine Portal é uma única aplicação Windows que lhe permite ligar-se, monitorizar e
organizar todas as máquinas da sua rede a partir de um só lugar — sem instalador, sem
configuração técnica.

<img width="952" height="715" alt="machine_portal_print" src="https://github.com/user-attachments/assets/a9420ab5-98e9-4360-912f-d604a0bace81" />

# [Apresentação](https://jorges15.github.io/MachinePortal/)

---

## O que faz

O Machine Portal reúne todas as suas máquinas num único painel. Cada máquina é um cartão que
mostra o nome, o número de série, o endereço IP e um indicador de estado ao vivo. Selecione uma
máquina e clique em **Ligar** e o ecrã remoto abre automaticamente — incluindo a criação de um
túnel SSH seguro nos bastidores, quando necessário. Pode pesquisar as máquinas, abrir a pasta de
uma máquina numa unidade de rede, guardar notas e fazer uma cópia de segurança de toda a lista
para a passar para outro PC.

---

## Funcionalidades

### Acesso remoto
- **Ligação num clique** — selecione uma máquina e clique em **Ligar**, ou faça duplo-clique no
  cartão. O ecrã remoto abre automaticamente e é encerrado sozinho quando o fecha.
- **Túnel SSH seguro** — as máquinas que precisam de túnel são tratadas de forma transparente. As
  credenciais nunca são mostradas em texto simples e ficam encriptadas no seu PC.
- **Estado ao vivo** — cada cartão mostra um ponto colorido, actualizado a cada poucos segundos:
  **verde** = acessível, **vermelho** = inacessível, **cinzento** = ainda não verificado.

### Gestão de máquinas
- **Adicionar, editar e remover** máquinas a qualquer momento.
- **Número de série e notas** em cada máquina, visíveis no cartão e pesquisáveis.
- **Barra de pesquisa** — filtre instantaneamente por nome, endereço IP ou número de série.
- **Imagem do cartão** — clique com o botão direito num cartão → *Alterar Imagem* para identificar
  cada máquina facilmente.
- **Menu do botão direito** em qualquer cartão: Ligar, Abrir pasta da máquina, Alterar Imagem,
  Editar, Remover.

### Pasta da máquina
- **Abrir pasta da máquina** abre a pasta dessa máquina na unidade de rede configurada (usando o
  número de série), pondo a documentação e os ficheiros a um clique de distância.

### Cópia de segurança e restauro
- **Exporte** a sua lista de máquinas e definições para um ficheiro `.json`, e **importe-a** noutro
  PC ou após uma reinstalação.
- Por segurança, as cópias de segurança **não incluem as palavras-passe SSH** (essas são
  encriptadas por PC e não podem ser restauradas noutro) — basta reintroduzi-las uma vez após o
  restauro.

### Ajuda incorporada
- **? Guia** — um passo-a-passo para cada tarefa, dentro da própria aplicação.
- **? Ajuda** — um formulário de suporte que envia a sua mensagem à Equipack com o registo (log)
  anexado.

### Personalização
- Temas **Claro e Escuro**.
- Interface em **Português e Inglês**.

### Seguro e licenciado
- **Licenciado por PC** — active uma vez com uma chave associada a este computador; não é preciso
  internet depois disso.
- **Credenciais encriptadas** — as palavras-passe SSH guardadas são protegidas com a encriptação
  da conta Windows.
- **Actualizações assinadas** — a aplicação só instala actualizações com uma assinatura válida da
  Equipack.

---

## Requisitos do sistema

| | |
|---|---|
| Sistema operativo | Windows 10 ou Windows 11 (64 bits) |
| Rede | Acesso à rede local das máquinas a que quer aceder |
| Instalação | Nenhuma — um único `.exe`, sem instalador |

---

## Primeiros passos

### 1. Activar a aplicação
No primeiro arranque, a janela de **Activação** mostra o seu **ID do Dispositivo** — um código
curto associado a este PC.
1. Clique em **Copiar** para copiar o ID do Dispositivo.
2. Envie-o ao seu fornecedor (Equipack).
3. Cole a chave de licença que receber e clique em **Activar**.

A licença fica guardada localmente; não é necessária ligação à internet após a activação.

### 2. Adicionar a primeira máquina
1. Clique em **+ Adicionar** no canto superior direito.
2. Introduza o **nome**, o **endereço IP** e o **número de série**.
3. Active o **túnel SSH** se a máquina precisar (o seu fornecedor indicará), e introduza o
   utilizador/palavra-passe SSH.
4. Clique em **Guardar** — o cartão aparece no painel.

### 3. Ligar
Clique num cartão para o selecionar e clique em **Ligar**, ou faça duplo-clique no cartão. O ecrã
remoto abre automaticamente. Feche-o quando terminar — a ligação encerra-se sozinha.

> Novo na aplicação? Abra **? Guia** na barra de ferramentas para os mesmos passos com mais
> detalhe, ou leia **[INSTRUCTIONS.md](INSTRUCTIONS.md)**.

---

## Utilização diária

- **Encontrar uma máquina** — escreva na barra de pesquisa (nome, IP ou série). A lista filtra à
  medida que escreve.
- **Abrir a pasta de uma máquina** — clique com o botão direito no cartão → *Abrir pasta da
  máquina* (requer o Caminho da Unidade de Rede definido nas Definições e um número de série na
  máquina).
- **Editar ou remover** — clique com o botão direito no cartão, ou selecione-o e use a barra de
  ferramentas.

---

## Definições

Abra as **Definições** para alterar:

| Definição | Descrição |
|---|---|
| Tema | Claro ou Escuro |
| Idioma | Inglês ou Português (PT) |
| Caminho da Unidade de Rede | Caminho de rede base usado por *Abrir pasta da máquina* |
| Porta VNC | Porta usada para ligações diretas (sem túnel) |
| Porta SSH Remota | A porta VNC no lado remoto do túnel |
| Espera do Túnel SSH | Tempo de espera pelo túnel antes de abrir o visualizador |
| Cópia de segurança / Restauro | Exportar ou importar a lista de máquinas num ficheiro `.json` |

---

## Actualizações

O Machine Portal verifica se há novas versões no arranque. Quando existe uma, propõe actualizar;
a transferência é verificada com a assinatura da Equipack antes de ser instalada, por isso só
correm versões genuínas. Também pode verificar manualmente nas **Definições**.

---

## Resolução de problemas

| Sintoma | O que tentar |
|---|---|
| O ponto de estado fica cinzento | A máquina pode estar inacessível, ou uma firewall bloqueia os pings da rede |
| A ligação falha | Verifique se o endereço IP está correto, se a máquina está ligada e (para SSH) o utilizador/palavra-passe |
| "Local port already in use" (porta local já em uso) | Uma sessão anterior pode estar aberta — feche-a, ou reinicie o Machine Portal |
| A janela de activação aparece sempre no arranque | Volte a activar; contacte o fornecedor se perdeu a chave de licença |

Se não conseguir resolver, use **? Ajuda** para enviar um pedido de suporte — o ficheiro de
registo é anexado automaticamente para um diagnóstico rápido.

---

## Suporte

**Equipack, Lda.** — Jorge Santos
jorgesantos@equipack.pt
