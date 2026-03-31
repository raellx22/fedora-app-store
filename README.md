<div align="center">
  <img src="data/fedora-app-store.png" alt="Fedora App Store Logo" width="150" height="150">
  <h1>Fedora App Store</h1>
  <p>Uma interface gráfica (GUI) elegante e moderna para instalação de aplicativos nativos no Fedora Linux.</p>
</div>

---

## 💡 Sobre o Projeto

O **Fedora App Store** nasceu de uma necessidade específica da comunidade: facilitar a vida dos usuários que preferem utilizar **pacotes nativos (RPM)** em vez de formatos em sandbox (como Flatpaks ou Snaps). 

O Fedora já possui uma excelente loja de aplicativos (GNOME Software), mas ela tem um forte viés para Flatpaks e esconde repositórios de terceiros. O objetivo deste projeto é fornecer uma vitrine direta, rápida e visualmente agradável para softwares extraídos nativamente de repositórios como:

- **RPM Fusion**
- **Fedora COPR** (Repositórios da Comunidade)
- **Terra Repositories**
- **Repositórios Oficiais de Empresas** (Google, Microsoft, Brave, etc.)

## ✨ Funcionalidades

- **Design Premium:** Interface totalmente escrita em GTK4 e Libadwaita, seguindo as diretrizes modernas do GNOME.
- **Ecossistema a um clique:** Tela inicial dedicada para habilitar rapidamente o RPM Fusion, suporte a Chrome e Steam.
- **Habilitação Automática de Repositórios:** Se um aplicativo precisa de um repositório COPR ou externo para funcionar, a loja habilita o repositório automaticamente antes da instalação.
- **100% Nativo:** Todos os scripts rodam via `dnf` em background. Nada de Flatpaks, garantindo que os aplicativos tenham integração máxima com o sistema e consumam menos espaço em disco.
- **Configuração Simples:** O catálogo de aplicativos é gerenciado inteiramente por um arquivo `apps.json`, tornando incrivelmente fácil para a comunidade adicionar novos softwares.

## 🚀 Instalação

A maneira mais fácil de instalar é baixando a versão empacotada (RPM) mais recente.

1. Vá até a página de [Releases](https://github.com/raellx22/fedora-app-store/releases) do repositório.
2. Baixe o arquivo `.rpm` da versão mais recente (ex: `fedora-app-store-1.0.0-1.fcXX.noarch.rpm`).
3. Instale o pacote dando um duplo-clique no arquivo baixado, ou usando o terminal:

```bash
sudo dnf install ./fedora-app-store-*.rpm
```

4. Após a instalação, basta procurar por "Fedora App Store" no menu de aplicativos do seu sistema!

## 🛠️ Para Desenvolvedores e Contribuidores

Se você deseja rodar a loja diretamente do código fonte ou adicionar novos aplicativos:

1. Clone o repositório:
```bash
git clone https://github.com/raellx22/fedora-app-store.git
cd fedora-app-store
```

2. Certifique-se de ter as dependências instaladas:
```bash
sudo dnf install python3 python3-gobject gtk4 libadwaita polkit
```

3. Execute o código:
```bash
python3 src/main.py
```

### Como adicionar um novo aplicativo?

Basta editar o arquivo `data/apps.json`. O formato é simples:

```json
{
    "nome-da-categoria": [
        {
            "name": "Nome do App",
            "package_name": "nome-do-pacote-dnf",
            "repo_cmd": "comando para habilitar o repo (opcional)",
            "repo_id": "identificador_do_repo.repo (opcional)",
            "icon": "nome-do-icone-do-sistema",
            "description": "Uma breve descrição sobre o app."
        }
    ]
}
```

## 📜 Licença

Este projeto é distribuído sob a licença [GPL-3.0](LICENSE), o que significa que ele é e sempre será de código aberto e livre para a comunidade.
