# Magnific: locução e imagens com IA

O [Magnific](https://www.magnific.com) (antigo Freepik) gera locução (vozes da ElevenLabs e do Gemini), imagens, vídeos e música. O kit usa o Magnific para duas coisas: **locução** e **imagens**. É opcional e pago: cada geração gasta créditos do plano de quem conectou.

**Cada pessoa usa a própria conta.** O kit não vem com chave nem conta. Quem clonar conecta o próprio Magnific (seção 1), e os créditos gastos são os dessa conta.

## 1. Conectar a sua conta

### Opção A, recomendada: MCP do Magnific (sem chave)

O MCP é a ponte que deixa o Claude Code usar o Magnific direto na conversa. Ele roda nos servidores do Magnific; não instala nada no computador.

No terminal (Windows ou Mac), uma vez só:

```bash
claude mcp add --transport http magnific https://mcp.magnific.com
```

Na primeira vez que o Claude usar uma ferramenta do Magnific, o navegador abre para você entrar na sua conta e aprovar o acesso. Não há chave para copiar. Quem usa o Claude no navegador ou no app também pode ligar o Magnific em Configurações > Conectores.

Conferir: peça ao Claude "qual o meu saldo de créditos no Magnific?". Ele chama `account_balance`.

### Opção B: API do Magnific (com chave própria)

Só para script fora do Claude, ou se a sua conta não puder usar o MCP.

1. Crie a chave no painel do Magnific: magnific.com > conta da organização > API Keys (precisa ser administrador da organização).
2. Guarde a chave num arquivo `.env` **fora da pasta do kit** (por exemplo, na pasta `.claude` do seu usuário), com o nome `MAGNIFIC_API_KEY`. Nunca dentro do projeto, no `storyboard.md` ou no chat.
3. A API fica em `https://api.magnific.com` e recebe a chave no cabeçalho `x-magnific-api-key`. Documentação: docs.magnific.com.

Pela API, toda geração cobra créditos da organização, mesmo em plano "ilimitado" (o ilimitado vale só dentro do site).

## 2. Regras de gasto (valem para as duas opções)

1. Antes de qualquer geração, rode `simulate_cost` com os mesmos argumentos e `account_balance`.
2. Diga ao usuário quantas gerações, o custo em créditos e o saldo, e **espere o "pode"**.
3. Teste primeiro com uma peça só (um vídeo, um idioma, uma imagem). Só faça o lote depois da aprovação do teste.
4. Ao entregar, diga quantos créditos foram gastos de fato (vem em `credits` na resposta da geração).

Referência de custo medida no kit: locução de 25 s com a ElevenLabs v4 custou de 62 a 72 créditos; uma frase curta refeita, 16.

## 3. Locução

O fluxo que usamos para pôr locução num vídeo de 25 a 40 s, com a fala no tempo das cenas.

1. **Copy por cena.** Escreva uma frase por cena, retomando os termos que aparecem na tela e acrescentando o que a tela não diz. Ritmo de anúncio: de 2,5 a 3 palavras por segundo de cena. Anote no `storyboard.md` (cena, tempo, texto da tela, fala). Mostre ao usuário antes de gerar.
2. **Escreva para ser falado:**
   - número por extenso e com a moeda dita: "quatro dólares e noventa e nove", não "$4.99" (sem a moeda, "quatro e noventa e nove" soa como reais em português);
   - nome de marca que a voz pode errar: teste numa frase curta; se errar, escreva como se pronuncia ou use IPA entre barras (por exemplo `/ˈnaɪki/` para Nike);
   - reticências dão pausa; MAIÚSCULAS dão ênfase.
3. **Modelo:** `eleven_v4` (o padrão, o mais natural). Chame `audio_tts_direction` com `model: "eleven_v4"` antes de escrever o texto: ele lê marcações de direção entre colchetes, por exemplo `[confident, upbeat ad read]` no começo.
4. **Voz:** `audio_voices_list` com `search` (por exemplo "male", "Spanish", "Portuguese"). A lista é enorme: salve numa pasta temporária e filtre por `gender`, `languages` e palavras da descrição como "advertising", "commercial", "promo". Prefira vozes nativas de cada idioma (espanhol latino para público dos EUA). Diga ao usuário quais escolheu.
5. **Uma gravação contínua por idioma**, com o texto de todas as cenas em sequência. Soa mais natural que frase por frase e custa o mesmo.
6. `simulate_cost`, "pode" do usuário, `audio_tts`, depois `creations_wait` até terminar.
7. **Baixe na hora** o `url` do resultado (é um link temporário) para `videos/<pasta>/bruto/gerado/<nn>-locucao-<idioma>.mp3`. Não grave o link em arquivo nenhum.
8. **Tempo de cada frase:** `audio_timing_get` devolve o início de cada palavra. Os cortes são os inícios da primeira palavra de cada cena, a partir da 2ª.
9. **Encaixar nas cenas:** `ferramentas/encaixar_locucao.py` (exemplo no começo do arquivo). Ele avisa quando uma frase atrasa a seguinte.
10. **Misturar:** receita 11 do `ferramentas/ffmpeg-receitas.md` (vídeo que já tem trilha) ou receita 6 (vídeo sem som, com a trilha do kit).
11. **Conferir:** transcreva a locução encaixada (`transcrever`) e compare com a copy: nenhuma palavra cortada, preço e marca certos. Depois o usuário ouve.
12. **Corrigir uma frase só:** gere só aquela frase com a mesma voz e emende no lugar (custa poucos créditos), em vez de refazer a gravação inteira.

Registre ao lado do arquivo um `<nn>-locucao-<idioma>.md` com serviço, modelo, voz, texto usado, duração e créditos cobrados.

## 4. Imagens

Para fundo de cena, ilustração, capa ou B-roll parado.

1. **Modelo:** `images_models_list` com `onlyRecommended: true`. Sem pedido do usuário, use `mode: "auto"`.
2. **Instrução (`prompt`)** nas palavras do usuário. Não acrescente estilo, luz ou câmera que ele não pediu.
3. **Formato:** `aspectRatio: "9:16"` para tela cheia de Reels; `"1:1"` ou `"4:5"` para um quadro dentro da tela. Várias opções de uma mesma ideia: uma chamada com `count` (até 8), nunca várias chamadas.
4. `simulate_cost`, "pode" do usuário, `images_generate`, `creations_wait`.
5. **Olhe o resultado** com `creations_read` antes de usar ou de gerar de novo. Texto dentro de imagem gerada costuma sair errado: texto na tela vai sempre pela composição do HyperFrames.
6. Baixe na hora para `videos/<pasta>/bruto/gerado/<nn>-imagem.png` e registre o `<nn>-imagem.md` (modelo, instrução, créditos).
7. Na composição, a imagem entra como qualquer outra mídia (`composicao/assets/img/`), respeitando a área segura.

**Não gerar:** rosto de pessoa real, logo ou produto de marca de terceiros, ou cena que pareça foto documental de algo que não aconteceu.

## 5. Problemas comuns

- **O Claude não encontra as ferramentas do Magnific:** rode o `claude mcp add` da seção 1 e reinicie o Claude Code. Se pedir login de novo, entre na conta no navegador que abrir.
- **"créditos insuficientes":** o saldo é o do plano da sua conta. Recarregar ou trocar de plano é decisão do usuário, no site do Magnific.
- **A voz pronuncia errado:** reescreva a palavra como se fala ou use IPA, e gere de novo só a frase.
- **A frase não cabe na cena:** encurte o texto da cena (tire palavras, não acelere a voz). O `eleven_v4` não aceita mudar a velocidade.
