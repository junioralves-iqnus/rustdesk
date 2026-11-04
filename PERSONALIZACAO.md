# Personalização visual do fork

> Esta versão também altera o nome público para **Suporte Iqnus**. Consulte [RENOMEACAO-IQNUS.md](RENOMEACAO-IQNUS.md) para aplicar e recompilar.

A logo fornecida foi aplicada em 70 recursos de marca. A cópia original recebida não foi alterada.

## Entrega e uso no seu Git

O projeto recebido era uma exportação sem pasta `.git` e com `libs/hbb_common` vazio. O pacote completo preserva essa condição: ele não contém histórico Git nem recupera o commit do submódulo, informação que não existe na exportação.

Para recompilar de forma reproduzível, use um clone do seu próprio fork na mesma revisão do código enviado. Extraia `rustdesk-personalizacao-alteracoes.zip` **na raiz desse clone**; esse arquivo contém somente os arquivos alterados/adicionados, sem pasta externa. Preserve a pasta `.git` e os submódulos do clone. O ZIP completo contém a pasta `rustdesk-personalizado/` com todos os arquivos recebidos mais a personalização.

Depois, na raiz do clone:

```sh
git submodule update --init --recursive
git status --short
git diff --stat
```

A regra do projeto que ignorava todos os PNG/SVG recebeu exceções específicas para os recursos gerados. Assim, os novos arquivos de logo entram no `git add` sem exigir `-f`. Revise as alterações antes de fazer commit e push normalmente.

Os recursos já estão gerados. Python/Pillow **não são necessários no CI** para compilá-los. Use os workflows e requisitos de compilação já existentes no seu fork. Em uma compilação local incremental, limpe o cache anterior (`cargo clean` na raiz e `flutter clean` dentro de `flutter/`) para evitar recursos antigos no executável. Gere novamente os arquivos intermediários exigidos pelo fluxo original antes de compilar.

## O que foi substituído

- **Windows, Flutter e Sciter:** `res/icon.ico`, `res/tray-icon.ico`, `flutter/windows/runner/resources/app_icon.ico` e `flutter/assets/icon.ico`. O executável Rust, o bootstrap portátil e o pré-processador MSI já referenciam `res/icon.ico`; essas referências foram conferidas. O MSI copia esse ícone para seus recursos durante o pré-processamento.
- **ICO verdadeiro:** cada arquivo contém imagens de 16, 24, 32, 48, 64, 128 e 256 px, DIB de 32 bits, cabeçalhos/dimensões válidos e máscaras AND explícitas. Não há PNG/JPEG simplesmente renomeado para `.ico`, nem quadros PNG comprimidos no contêiner. Isso evita a incompatibilidade de formato relacionada ao RC2175; o compilador Microsoft RC não foi executado neste ambiente.
- **macOS:** `flutter/macos/Runner/AppIcon.icns`, utilizado pelo projeto Xcode e pelo Info.plist, mais `res/icon.icns`, `res/mac-icon.png` e ícones transparentes para a barra de menu. O ICNS possui representações de 32 a 1024 px, incluindo variantes Retina. O empacotamento Sciter usa os PNG declarados em `Cargo.toml`, também substituídos.
- **Linux:** PNG de 32/64/128/256 px e `res/scalable.svg`, usados pelos pacotes DEB, RPM, Arch e AppImage. Foram preservados os nomes dos arquivos e referências de instalação.
- **Flutter:** ícone PNG, fallback SVG e logos normal/clara/escura. A imagem fornecida permanece com suas cores e fundo nos dois temas.
- **Android:** launcher, launcher redondo, foreground adaptativo, versão monocromática e notificação em todas as cinco densidades. A notificação usa silhueta branca com fundo transparente; o foreground respeita a área segura circular. Os XML apontam para a versão monocromática e o fundo azul da marca.
- **iOS:** todos os 15 ícones declarados no catálogo, incluindo o de 1024 px, com dimensões corretas e sem canal alfa.
- **Documentação e loja:** SVG de cabeçalho/banner/design e ícone Android do Fastlane.
- **Sciter:** as duas logos PNG embutidas em base64 em `src/ui.rs`, incluindo a variante com margem para macOS.

Os SVG foram vetorizados em duas cores a partir da silhueta do PNG, sem raster embutido, para funcionar também no `flutter_svg`. Os PNG mantêm a imagem raster original redimensionada. As diferenças de antialiasing entre vetor e raster são esperadas.

A etapa inicial de ícones preservou o nome do aplicativo; a etapa documentada em `RENOMEACAO-IQNUS.md` agora o altera para Suporte Iqnus. IDs de pacote, servidores, URLs, licenças e créditos permanecem preservados. Ícones de ação, marcas de provedores de autenticação e símbolos dos sistemas operacionais foram preservados. Capturas de tela do Fastlane/documentação e ilustrações de ajuda também foram preservadas: são imagens de conteúdo, e devem ser recapturadas após executar o aplicativo personalizado. As telas de abertura vazias/placeholder do Android/iOS e o texto genérico de carregamento do portátil permanecem como no projeto recebido. Não havia diretório `flutter/web` na exportação; não foi criada uma versão web incompleta.

## Regenerar usando Pillow

O script foi escrito e executado nesta entrega com Python 3 e Pillow 10.2.0. Ele usa apenas Pillow e a biblioteca padrão. O método de extração de silhueta foi ajustado à sua logo, que tem fundo uniforme; revise o resultado ao utilizar uma arte com composição diferente.

```sh
python3 -m pip install Pillow
python3 res/customize_branding.py
```

O comando usa `res/branding-source.png`. Para trocar a arte:

```sh
python3 res/customize_branding.py /caminho/para/nova-logo.png
```

No Windows, use `py -3` no lugar de `python3`. Em Linux/macOS também pode usar `bash res/gen_icon.sh`, que chama o mesmo gerador. O script atualiza as imagens, as duas strings embutidas do Sciter, os XML relacionados e as exceções de Git. A lista exata de imagens está em `res/branding-manifest.json`.

## Verificação realizada

Foram verificados os 70 recursos: assinatura e decodificação dos PNG, estrutura de todos os quadros ICO e respectivas máscaras, cabeçalho/blocos ICNS, XML Android, SVG, dimensões e modo RGB do catálogo iOS, transparência dos ícones de notificação/bandeja, área segura adaptativa e inclusão dos recursos pelo Git. ImageMagick também decodificou independentemente os 28 quadros dos quatro ICO. A fonte preserva exatamente os pixels da imagem fornecida. Foi inspecionada uma prévia visual dos principais recursos.

A compilação completa não foi executada: este ambiente não possui Rust/Cargo, Flutter, Microsoft RC nem Xcode/SDKs de plataforma, e o submódulo `hbb_common` está ausente no material recebido. A validação dos recursos não equivale a uma validação integral dos executáveis.

## Superfície de regressão

As mudanças de comportamento em código existente se limitam a:

1. `src/ui.rs`: substituição das duas imagens base64 retornadas por `get_icon()`. Necessária para trocar o ícone de janelas/diálogos Sciter, que não vinha dos arquivos em `res/`.
2. `src/tray.rs`: no macOS, a imagem externa passa de `assets/icon.png` para `assets/mac-tray.png`. Necessária porque a bandeja usa modo template e interpreta somente o alfa; uma logo com fundo opaco viraria um quadrado. Windows e Linux continuam usando o caminho existente.
3. Dois XML de ícone adaptativo Android e o XML da sua cor de fundo: direcionam a versão monocromática e o fundo da marca.
4. `.gitignore`: permite versionar os PNG/SVG gerados, sem liberar imagens arbitrárias.
5. `res/gen_icon.sh`: delega ao gerador Pillow em vez de usar nomes intermediários inexistentes do script antigo.

Os demais arquivos existentes alterados são recursos visuais. Nenhuma lógica de conexão, acesso remoto, autenticação, instalação ou atualização foi modificada. A relação completa de arquivos e hashes acompanha a entrega em `verificacao-personalizacao.json`.
