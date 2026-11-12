#!/usr/bin/env bash
# Publica o projeto na conta autenticada e convida o colaborador.
set -Eeuo pipefail

usage() {
    printf '%s\n' \
        'Uso: bash publicar_github.sh [nome-do-repositorio] [colaborador]' \
        'Padrões: projeto-amns-equipe08 rRodrigoGomes' \
        'Requisitos: Git e GitHub CLI (gh).' \
        'No Ubuntu/Debian, instale o CLI com: sudo apt install gh' \
        'O login, se necessário, será realizado pelo navegador.' \
        'Publica a branch main em um repositório privado e concede acesso de escrita.' \
        'Alterações locais devem estar commitadas antes da execução.'
}

fail() { printf 'Erro: %s\n' "$*" >&2; exit 1; }
trap 'printf "Operação interrompida na linha %s. Verifique o erro acima; etapas concluídas são preservadas.\n" "$LINENO" >&2' ERR

if [[ ${1:-} == '--help' || ${1:-} == '-h' ]]; then
    usage
    exit 0
fi
[[ $# -le 2 ]] || { usage; exit 1; }
repo_name=${1:-projeto-amns-equipe08}
collaborator=${2:-rRodrigoGomes}
[[ $repo_name =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail 'Nome de repositório inválido.'
[[ $collaborator =~ ^[A-Za-z0-9][A-Za-z0-9-]*$ ]] || fail 'Informe o usuário do GitHub, sem @.'

command -v git >/dev/null || fail 'Instale o Git antes de continuar.'
command -v gh >/dev/null || fail 'Instale o GitHub CLI: sudo apt install gh. Depois execute este script novamente.'
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
cd -- "$project_dir"
[[ $(git rev-parse --show-toplevel) == "$project_dir" ]] || fail 'Execute no repositório deste projeto.'
git rev-parse --verify HEAD >/dev/null || fail 'Crie o primeiro commit antes de publicar.'
[[ $(git symbolic-ref --quiet --short HEAD) == main ]] || fail 'Mude para a branch main antes de publicar.'
[[ -z $(git status --porcelain) ]] || fail 'Há alterações sem commit. Revise e faça o commit antes de publicar.'

export GH_HOST=github.com
if ! gh auth status --hostname github.com >/dev/null 2>&1; then
    printf 'Autentique sua conta no navegador seguindo as instruções do GitHub.\n'
    gh auth login --hostname github.com --git-protocol https --web
fi
owner=$(gh api --hostname github.com user --jq '.login')
full_name="$owner/$repo_name"
repo_url="https://github.com/$full_name.git"
printf 'Conta autenticada: %s\nRepositório: %s\nColaborador: %s\n' "$owner" "$full_name" "$collaborator"
[[ ${owner,,} != ${collaborator,,} ]] || fail 'O colaborador é o proprietário autenticado; não há convite a enviar.'
gh api --hostname github.com "users/$collaborator" --jq '.login' >/dev/null

# Não troca um origin existente nem publica em um destino diferente por engano.
if git remote | grep -qx origin; then
    while IFS= read -r remote_url; do
        case "$remote_url" in
            "https://github.com/$full_name"|"$repo_url"|"git@github.com:$full_name"|"git@github.com:$full_name.git") ;;
            *) fail 'O origin aponta para outro repositório. Revise-o antes de executar novamente.' ;;
        esac
    done < <(git remote get-url --all origin; git remote get-url --push --all origin)
fi

# Uma falha de autenticação ou de rede encerra a operação, em vez de ser
# interpretada como ausência do repositório.
existing=$(gh api --hostname github.com --paginate \
    'user/repos?affiliation=owner&per_page=100' \
    --jq ".[] | select((.name | ascii_downcase) == (\"$repo_name\" | ascii_downcase)) | .full_name")
if [[ -z $existing ]]; then
    gh repo create "$full_name" --private \
        --description 'Projeto de Aprendizado de Máquina Não Supervisionado — Equipe 08: Iris, agrupamento e redução de dimensionalidade.'
else
    printf 'Repositório existente encontrado: %s\n' "$existing"
fi
private_admin=$(gh api --hostname github.com "repos/$full_name" --jq '.private and .permissions.admin')
[[ $private_admin == true ]] || fail 'O destino precisa ser privado e sua conta precisa ter permissão de administrador.'

if ! git remote | grep -qx origin; then
    git remote add origin "$repo_url"
fi
# Configuração restrita ao repositório: usa o login do gh no push HTTPS.
git config --local credential.https://github.com.helper ''
git config --local --add credential.https://github.com.helper '!gh auth git-credential'
# Usa a URL validada em HTTPS mesmo quando origin foi configurado com SSH.
# Não força o push: históricos incompatíveis interrompem a execução.
git push "$repo_url" main:main
git fetch "$repo_url" refs/heads/main:refs/remotes/origin/main
git branch --set-upstream-to=origin/main main

members=$(gh api --hostname github.com --paginate "repos/$full_name/collaborators?per_page=100" \
    --jq '.[].login')
if printf '%s\n' "$members" | grep -Fxiq -- "$collaborator"; then
    printf '%s já é colaborador; as permissões existentes foram preservadas.\n' "$collaborator"
else
    pending=$(gh api --hostname github.com --paginate "repos/$full_name/invitations?per_page=100" \
        --jq '.[].invitee.login')
    if printf '%s\n' "$pending" | grep -Fxiq -- "$collaborator"; then
        printf 'Já existe um convite pendente para %s.\n' "$collaborator"
    else
        gh api --hostname github.com --method PUT \
            "repos/$full_name/collaborators/$collaborator" \
            -f permission=push --silent
        printf 'Convite com acesso de escrita enviado para %s. Ele precisa aceitá-lo.\n' "$collaborator"
    fi
fi
printf 'Projeto publicado: https://github.com/%s\n' "$full_name"
