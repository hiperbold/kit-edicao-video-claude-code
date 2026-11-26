# Design systems

Cada pasta aqui é um design system pronto (uma marca, um cliente, uma linha visual). O vídeo usa o que estiver escolhido no `marca.json` da raiz.

## Estrutura de um design system

```
design-systems/<nome>/
  marca.json        cores, fontes, logo e cartão final (mesmo formato do marca.exemplo.json;
                    caminhos a partir DESTA pasta: "logos/...", "fontes/...")
  regras.md         como usar em vídeo: cor para cada coisa, tipografia, logo, tom, o que evitar
  logos/            logos em SVG (de preferência) ou PNG transparente; versão clara e escura
  fontes/           arquivos de fonte (.ttf, .otf, .woff2)
  referencia/       material original do design system (HTML, PDF, prints), só para consulta
```

Nome da pasta: minúsculas, com hífen, sem acento nem espaço (funciona igual no Windows e no Mac).

## Usar um design system

No `marca.json` da raiz:

```json
{ "designSystem": "<nome>" }
```

Os scripts (`reels.mjs`, `capa.mjs`) leem `design-systems/<nome>/marca.json`. O que mais estiver no `marca.json` da raiz vale por cima (por exemplo, um `cartaoFinal` diferente para uma campanha): por isso, deixe nele só o `designSystem` e o que quiser trocar de propósito. Sem `designSystem`, vale o `marca.json` da raiz como antes.

Para trocar de marca entre um vídeo e outro, troque o nome em `designSystem`. Anote no `storyboard.md` de cada vídeo qual design system ele usou.

## Trazer um design system que já existe

1. Crie `design-systems/<nome>/` copiando a pasta `exemplo/`.
2. Ponha os logos em `logos/` e as fontes em `fontes/`.
3. Copie para `referencia/` o material original (o HTML do design system, PDF do manual, prints).
4. Preencha o `marca.json` com as cores e fontes do design system. Os nomes das cores (`fundo`, `marinho`, `acento`, `acao`, `creme`, `cinza`) são os que os scripts usam: encaixe as cores do design system nesses papéis.
5. Preencha o `regras.md` a partir do material de `referencia/`.
6. Confira com o `exemplo/` do kit (`exemplo/README.md`) e a capa: cores, fontes e logo certos.

## Privacidade

Design system de cliente pode ser confidencial e fonte paga pode não permitir distribuição. Se a sua pasta do kit vai para um repositório público, deixe essas pastas fora do git: acrescente `design-systems/<nome>/` ao `.gitignore`.
