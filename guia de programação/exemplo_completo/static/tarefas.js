// HTML mostra os dados; JavaScript controla busca e popup; Python grava.
const tarefas = JSON.parse(document.getElementById("tarefas-data").textContent);
const dialog = document.getElementById("editor");
const form = document.getElementById("form-tarefa");
let botaoOrigem;

function abrir(tarefa, origem) {
  botaoOrigem = origem;
  form.reset();
  form.action = tarefa ? `/tarefas/${tarefa.id}/editar` : "/tarefas";
  document.getElementById("titulo-editor").textContent = tarefa ? `Editar tarefa #${tarefa.id}` : "Nova tarefa";
  if (tarefa) {
    for (const campo of ["titulo", "descricao", "status", "prioridade", "fiscal_id"]) {
      form.elements.namedItem(campo).value = tarefa[campo];
    }
  }
  dialog.showModal(); // dialog nativo controla foco e tecla Escape
  form.elements.namedItem("titulo").focus();
}

document.getElementById("nova-tarefa").addEventListener("click", event => abrir(null, event.currentTarget));
document.querySelectorAll(".editar").forEach(button => button.addEventListener("click", () => {
  const tarefa = tarefas.find(item => item.id === Number(button.dataset.id));
  if (tarefa) abrir(tarefa, button);
}));
document.querySelectorAll(".fechar").forEach(button => button.addEventListener("click", () => dialog.close()));
dialog.addEventListener("close", () => botaoOrigem?.focus());
document.querySelectorAll(".excluir").forEach(formExcluir => formExcluir.addEventListener("submit", event => {
  if (!window.confirm("Excluir esta tarefa do exemplo?")) event.preventDefault();
}));
document.getElementById("busca").addEventListener("input", event => {
  const termo = event.target.value.trim().toLocaleLowerCase("pt-BR");
  let visiveis = 0;
  document.querySelectorAll("tr[data-search]").forEach(row => {
    row.hidden = !row.dataset.search.includes(termo);
    if (!row.hidden) visiveis++;
  });
  document.getElementById("vazio").hidden = visiveis > 0;
});
