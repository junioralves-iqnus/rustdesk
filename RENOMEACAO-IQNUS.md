# Nome público: Suporte Iqnus

Esta entrega usa como base o projeto mais recente enviado, localizado em `rustdesk-master/rustdesk-master/`. O nome exibido passa a ser **Suporte Iqnus**, mantendo a logo e os ícones já personalizados. A pasta original enviada não foi modificada.

## Aplicar no seu fork e recompilar

O pacote `suporte-iqnus-alteracoes.zip` contém somente as alterações desta etapa, sem pasta externa. Extraia seu conteúdo na raiz de um clone do seu fork na mesma revisão do material enviado, preservando `.git`. O pacote `suporte-iqnus-projeto.zip` contém a cópia completa, dentro de `suporte-iqnus/`.

O material recebido continua sem histórico `.git` e com o submódulo `libs/hbb_common` vazio. No clone do seu fork, execute:

```sh
git submodule update --init --recursive
git status --short
git diff --stat
```

Depois faça commit/push e use o fluxo de compilação existente. Os nomes técnicos dos artefatos e executáveis permanecem compatíveis com os scripts atuais.

Em uma árvore que já compilou a versão anterior, limpe os recursos antigos antes de recompilar:

```sh
cargo clean
cd flutter
flutter clean
```

Siga o fluxo original para reinstalar dependências e gerar os arquivos intermediários necessários após a limpeza. O ambiente desta entrega não possui Rust/Cargo, Flutter, Microsoft RC nem Xcode/SDKs; portanto os executáveis finais não foram compilados aqui.

## Para o nome aparecer no aplicativo instalado

Alterar o código-fonte não modifica uma instalação existente. Recompile e instale o novo pacote. No Windows, use a mesma modalidade do pacote anterior: o projeto não suporta instalar EXE por cima de MSI. Use MSI sobre MSI ou o instalador EXE correspondente.

- **Pesquisa do Windows e atalhos:** a instalação nova cria `Suporte Iqnus.lnk` e a pasta pública `Suporte Iqnus` no menu Iniciar. O instalador EXE também remove os atalhos de sistema com o nome antigo. Atalhos criados/copiedos manualmente e atalhos fixados em um perfil podem permanecer; remova o antigo e fixe novamente o novo atalho.
- **Tooltip da bandeja e títulos das janelas:** feche a instância antiga, inclusive a bandeja, e abra a nova instalação. A instância nova informa `Suporte Iqnus`.
- **Propriedades do executável:** `ProductName` e `FileDescription` passam a `Suporte Iqnus`. O nome físico interno `rustdesk.exe` permanece para compatibilidade com o instalador e atualizador.
- **Linux:** reinstale o pacote e abra pelo novo item `Suporte Iqnus`. O arquivo técnico continua `rustdesk.desktop`, preservando a associação entre janela e launcher. Um item fixado anteriormente pode precisar ser removido e adicionado novamente.
- **macOS:** os nomes públicos `CFBundleDisplayName` e `CFBundleName` passam a `Suporte Iqnus`. A pasta técnica do bundle continua `RustDesk.app`, preservando o fluxo de assinatura, instalação e atualização. No Sciter, use `build.py` para aplicar os metadados após `cargo bundle`, antes da assinatura. Um `cargo bundle` executado isoladamente não executa essa etapa adicional.
- **Android/iOS:** recompile e instale a nova versão para atualizar o rótulo exibido pelo sistema.

Não foram alterados nomes de serviços internos, esquemas `rustdesk://`, extensões, IDs de pacote, nomes de bibliotecas, diretórios de configuração, dependências, servidores nem licenças. O serviço pode continuar identificado internamente como `RustDesk`, com nome público `Suporte Iqnus Service`. Isso permite conservar as configurações e as referências de atualização. Esta personalização compartilha a identidade técnica do fork anterior; não foi criada uma instalação paralela independente.

## Superfície de alteração e motivo

Cada alteração existente foi revisada para restringir a mudança ao nome público e às referências necessárias para seu funcionamento:

| Arquivos existentes | Comportamento alterado e motivo |
| --- | --- |
| `src/common.rs` | Adiciona a constante `APP_DISPLAY_NAME` e o acesso ao nome público; preserva `get_app_name()` interno. |
| `src/tray.rs` | Troca apenas o nome no tooltip da bandeja. |
| `src/ui.rs`, `src/ui/index.tis` | Título, menu Sobre e aviso de atualização Sciter usam o nome público; o método interno continua disponível para instalação. |
| `src/flutter.rs`, `src/core_main.rs`, `flutter/windows/runner/main.cpp` | Título nativo e procura de janela existente usam o mesmo nome público; mantém o encaminhamento de links e o comportamento de instância única. Também atualiza o título dos avisos de instalação/atualização. |
| `src/lang.rs` | Usa o mecanismo existente de substituição de marca para mostrar o nome público nos textos traduzidos, preservando suas exclusões para referências de servidor/créditos. Não modifica os catálogos de tradução. |
| `src/platform/delegate.rs` | Mostra o nome público na opção de sair do menu macOS. |
| `flutter/lib/common.dart`, `flutter/lib/main.dart`, `flutter/lib/desktop/pages/desktop_home_page.dart`, `flutter/lib/mobile/pages/home_page.dart` | Define `appDisplayName` e aplica o nome aos títulos principais, janelas auxiliares e aviso de nova versão. A bridge interna de nomes permanece igual. |
| `flutter/lib/desktop/pages/desktop_setting_page.dart`, `flutter/lib/desktop/pages/install_page.dart`, `flutter/lib/desktop/widgets/update_progress.dart`, `flutter/lib/desktop/widgets/tabbar_widget.dart` | Aplica a marca nos textos de instalação, configuração, atualização e no título fixo da barra de abas. |
| `src/platform/windows.rs` | Nome de atalhos/pasta do menu Iniciar, registro DisplayName e nomes públicos de serviço. Atualiza a cópia/limpeza dos atalhos para os nomes novos, preservando a remoção dos antigos. Executáveis, serviço interno, registro técnico e regras de firewall permanecem com seus identificadores originais. |
| `src/platform/windows/installer_shell.rs` | Define uma descrição pública nos atalhos para o tooltip. |
| `src/platform/windows/msi_registry.rs` | Reconhece também o MSI com DisplayName novo, mantendo a descoberta para desinstalação/atualização. Sem isso, renomear o produto impediria localizar o MSI por seu nome anterior. |
| `Cargo.toml`, `libs/portable/Cargo.toml`, `flutter/windows/runner/Runner.rc` | Atualiza ProductName/FileDescription dos executáveis Rust, portátil e Flutter. Não altera nomes de crate, biblioteca ou OriginalFilename. |
| `flutter/windows/runner/service_control.h`, `res/msi/CustomActions/CustomActions.cpp` | Nome público do serviço nas rotas nativas EXE e MSI; nome técnico do serviço preservado. |
| `res/msi/preprocess.py`, `res/msi/Package/Package.wxs`, `res/msi/Package/Components/Folders.wxs` | Gera ProductDisplayName separado do Product técnico; aplica o nome à apresentação do MSI e à pasta do menu. Preserva UpgradeCode, executável, caminhos técnicos e placeholder do template MSI. |
| `res/rustdesk.desktop`, `res/rustdesk-link.desktop`, `res/rustdesk.service`, `flutter/linux/my_application.cc`, `flatpak/com.rustdesk.RustDesk.metainfo.xml` | Nomes de menu, pesquisa, janela, descrição do serviço e catálogo Linux; mantém Exec, Icon, WMClass e IDs técnicos. |
| `flutter/macos/Runner/Info.plist`, `flutter/macos/Runner/Base.lproj/MainMenu.xib`, `build.py` | Nome público do bundle e menus Flutter; metadados do bundle Sciter antes da assinatura. O nome do módulo Swift, o executável e os caminhos de build permanecem iguais. |
| `flutter/ios/Runner/Info.plist`, `flutter/android/app/src/main/AndroidManifest.xml`, `flutter/android/app/src/main/res/values/strings.xml` | Nome público dos apps móveis e descrições Android associadas. |
| `.gitignore` | Restaura exceções específicas dos recursos de marca, para que novas imagens entrem no Git. |

Também foram restaurados dez arquivos PNG ausentes no material mais recente: a fonte da marca, as três logos Flutter, a silhueta de bandeja macOS e as cinco versões monocromáticas Android. Essas imagens já haviam sido geradas na etapa anterior. Todos os arquivos de imagem que já existiam no projeto mais recente permaneceram idênticos byte a byte.

`PERSONALIZACAO.md` recebeu uma indicação desta etapa; o relatório da etapa anterior permanece como registro da validação dos ícones. `verificacao-nome.json` contém o inventário atualizado de arquivos, hashes e verificações desta entrega.

## Validação realizada

- `desktop-file-validate` aprovou os dois atalhos Linux.
- Foram interpretados os TOML, plist e XML alterados e conferidos nomes públicos e identificadores técnicos.
- O pré-processador MSI real foi executado sobre cópias das fontes: gerou `ProductDisplayName="Suporte Iqnus"`, atalhos e descrições novos, mantendo `Product="RustDesk"`, `ProductLower="rustdesk"` e o mesmo UpgradeCode. O placeholder `RDAPPNAM` do template também foi conferido.
- Foram conferidas em conjunto as referências de título nativo, título Dart e busca de janela existente no Windows, além da apresentação Sciter e do tooltip de bandeja.
- Os 70 recursos de marca estão presentes e são aceitos pelo Git; os PNG/ICO/ICNS foram decodificados e o ImageMagick leu independentemente os 28 quadros ICO.
- Regenerar as imagens com Pillow não altera a personalização do nome nem qualquer outro arquivo da cópia final.
- Dependências, licenças, identidade técnica e todas as imagens preexistentes foram comparadas com a origem.

Essas verificações são de fontes, metadados e geração de recursos. Não substituem testar a compilação e a instalação em cada sistema operacional.
