# Migrações de estrutura

Cada mudança de estrutura exigida por uma versão da aplicação deve incluir
um novo arquivo SQL nesta pasta, como `0002_descricao.sql`. O instalador
executa os arquivos em ordem e registra nome, SHA256 e data em
`public.app_schema_migrations`, dentro da mesma transação das alterações.

- Nunca edite ou remova uma migração já publicada; acrescente outra versão.
- Preserve os dados e as colunas existentes. Prefira adicionar tabelas,
  colunas e índices. Não inclua `DROP TABLE`, `DROP COLUMN`, `TRUNCATE` ou
  exclusões de registros para ajustar a estrutura ao banco local.
- Para renomear ou converter campos, planeje uma migração que mantenha a
  informação original e valide a conversão; não descarte os campos antigos.
- A primeira migração cobre as adições de campos de eventos e contatos e a
  tabela de faixas de etiquetas. Ela pressupõe as tabelas-base da aplicação
  existentes e não tenta reconstruir versões históricas arbitrárias.
- Alterar somente `db/schema.sql` não atualiza um servidor existente. Esse
  arquivo contém operações legadas de remoção e não é executado no envio.
- Teste novas migrações com dados existentes, inclusive valores nulos,
  duplicidades e registros criados exclusivamente no servidor.

Nas atualizações, o instalador pausa a aplicação, clona o banco do servidor
e aplica as migrações nessa cópia. Uma falha de SQL descarta a transação.
O banco original permanece disponível para recuperação. Na primeira
instalação em um banco sem tabelas, o backup local fornece a estrutura e os
dados iniciais antes de aplicar as migrações.
