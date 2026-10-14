"""Instala a análise espacial descritiva de filas no tc-valdir.

Biblioteca padrão; não executa git, SUMO ou os analisadores. Confere todos os
conflitos antes de copiar e não substitui arquivos com conteúdo diferente.
"""
from pathlib import Path
import argparse, hashlib, json, shutil

IGNORE_MARKER = b"# Analise espacial de filas versionada - TC"
IGNORE_LINES = [
    "# Analise espacial de filas versionada - TC",
    "!output/analise/",
    "!output/analise/baseline_v1_filas_espacial_v1/",
]
MANIFEST = Path("docs/entrega-espacial-filas-v1.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install(package, repository, verify_only=False):
    package, repository = package.resolve(), repository.resolve()
    if not (repository / ".git").exists():
        raise ValueError("O destino precisa ser a raiz do repositório Git local")
    source_manifest = package / MANIFEST
    metadata = json.loads(source_manifest.read_text(encoding="utf-8"))
    entries = dict(metadata["files_sha256"])
    entries[MANIFEST.as_posix()] = sha(source_manifest)
    plan, conflicts = [], []
    for relative, expected_hash in entries.items():
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts or relative_path.parts[0] not in {"scripts", "docs", "testes", "output"}:
            raise ValueError(f"Caminho não permitido na entrega: {relative}")
        source = (package / relative_path).resolve()
        target = (repository / relative_path).resolve()
        if not source.is_relative_to(package) or not target.is_relative_to(repository):
            raise ValueError(f"Caminho escapa da pasta prevista: {relative}")
        if not source.is_file() or sha(source) != expected_hash:
            raise ValueError(f"Arquivo da entrega ausente/alterado: {relative}")
        if target.exists():
            if not target.is_file() or sha(target) != expected_hash:
                conflicts.append(relative)
        else:
            for parent in target.parents:
                if parent == repository:
                    break
                if parent.exists() and not parent.is_dir():
                    conflicts.append(relative)
                    break
            plan.append((source, target))
    if conflicts:
        raise ValueError("Nenhum arquivo copiado. Conteúdo diferente já existe em:\n" + "\n".join(sorted(set(conflicts))))
    if verify_only:
        print(f"Verificação concluída: {len(plan)} arquivos novos; {len(entries)-len(plan)} já idênticos. Nenhuma alteração realizada.")
        return
    for source, target in plan:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    ignore_path = repository / ".gitignore"
    original = ignore_path.read_bytes() if ignore_path.exists() else b""
    ignore_changed = False
    if IGNORE_MARKER not in original:
        newline = b"\r\n" if b"\r\n" in original else b"\n"
        block = newline.join(line.encode("ascii") for line in IGNORE_LINES) + newline
        ignore_path.write_bytes(original + newline + newline + block)
        ignore_changed = True
    readme = repository / "README.md"
    original_readme = readme.read_bytes() if readme.exists() else b"# TC - Valdir\n"
    updated = original_readme
    if b"docs/checkpoint-filas-espacial-2026-10-14.md" not in updated:
        newline = b"\r\n" if b"\r\n" in updated else b"\n"
        block = ["## Analise espacial das filas", "",
                 "Localizacao e comparacoes descritivas: [checkpoint espacial](docs/checkpoint-filas-espacial-2026-10-14.md).",
                 "Todas as 630 execucoes e 198 faixas preservadas; nomes com origem documentada."]
        updated += newline + newline + newline.join(line.encode("utf-8") for line in block) + newline
    if updated != original_readme:
        readme.write_bytes(updated)
    print(f"Instalação concluída: {len(plan)} arquivos novos; {len(entries)-len(plan)} já idênticos.")
    print("Exceções do .gitignore adicionadas." if ignore_changed else "Exceções do .gitignore já presentes.")
    print("Nenhum commit ou push foi executado. Consulte docs/README-filas-espacial.md para versionar. Nenhuma simulacao ou analise foi executada pelo instalador.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repositorio", type=Path, default=Path.cwd())
    parser.add_argument("--verificar", action="store_true", help="Conferir sem copiar ou editar")
    args = parser.parse_args()
    install(Path(__file__).resolve().parents[1], args.repositorio, args.verificar)


if __name__ == "__main__":
    main()
