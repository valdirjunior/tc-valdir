# Classificação das entradas e saídas da rede

Este documento registra a classificação qualitativa das edges utilizadas como
origens e destinos para a geração da demanda no cenário da Praça Nereu Ramos.

A classificação é utilizada apenas para definir pesos relativos na geração dos
veículos. Os valores não representam contagens reais de tráfego.

## Categorias de fluxo — versão em avaliação

| Categoria | Peso |
|---|---:|
| Muito alto | 5 |
| Alto | 4 |
| Médio | 3 |
| Baixo | 2 |
| Muito baixo | 1 |

> Os pesos 5/4/3/2/1 são uma configuração candidata para os testes
> preliminares. A classificação das vias ainda pode ser ajustada antes da
> definição final da demanda.

---

# Origens — entradas na rede

| Edge | Via / referência | Classificação anterior | Nova classificação | Peso | Observação |
|---|---|---|---|---:|---|
| `-1377929346#0` | Saul Brandalise | Alto | Muito alto | 5 | Uma das principais entradas da região |
| `320316411#0.175` | Av. Dom Pedro II | Alto | Muito alto | 5 | Entrada principal |
| `-E4` | XV de Novembro | Alto | Muito alto | 5 | Nova entrada incluída com a ampliação da rede |
| `-103925179#1` | Rua Brasil | Médio | Médio | 3 | Rever conforme distribuição observada |
| `99643286#2` | XV de Novembro | Médio | Médio | 3 | Acesso secundário pela XV |
| `-102361495#0` | Antônio Marafon | Baixo | Baixo | 2 | Entrada local |
| `-102361574.302` | Osvaldo Cruz | Baixo | Muito baixo | 1 | Entrada local |
| `99631677` | Santa Catarina | Baixo | Muito baixo | 1 | Entrada local |
| `-E5` | Farroupilha | Baixo | Muito baixo | 1 | Nova entrada incluída |
| `-E6` | Nicolau Cavon | Baixo | Muito baixo | 1 | Nova entrada incluída |

---

# Destinos — saídas da rede

| Edge | Via / referência | Classificação anterior | Nova classificação | Peso | Observação |
|---|---|---|---|---:|---|
| `1377929346#0.14` | Saul Brandalise | Alto | Muito alto | 5 | Saída principal; não deve formar OD Saul → Saul |
| `E4` | XV de Novembro | Alto | Muito alto | 5 | Saída principal; não deve formar OD XV → XV |
| `-99643286#2` | XV de Novembro | Médio | Alto | 4 | Rever distribuição em relação às demais saídas |
| `103925179#1` | Rua Brasil | Médio | Médio | 3 | Visualmente parece receber fluxo elevado; revisar |
| `99429213#1` | Antônio Fávero / acesso nessa direção | Médio | Baixo | 2 | Visualmente parece receber fluxo elevado; revisar |
| `102361495#0` | Antônio Marafon | Baixo | Baixo | 2 | Saída local |
| `102361574` | Osvaldo Cruz | Baixo | Muito baixo | 1 | Saída local |
| `103925196#0` | Padre Anchieta | Baixo | Muito baixo | 1 | Saída local |
| `E5` | Farroupilha | Baixo | Muito baixo | 1 | Nova saída incluída |
| `E6` | Nicolau Cavon | Baixo | Muito baixo | 1 | Nova saída incluída |
| `E8` | Sete de Setembro | Baixo | Muito baixo | 1 | Nova saída incluída |
| `E9` | Duque de Caxias | Baixo | Muito baixo | 1 | Nova saída incluída |

---

# Pares origem-destino a evitar

Algumas combinações foram identificadas nos testes como viagens que entram na
rede por uma via e retornam à mesma região de onde partiram. Essas rotas são
tecnicamente válidas para o roteador, mas podem produzir deslocamentos
artificiais para o recorte utilizado no trabalho.

## Pares já identificados

| Origem | Destino | Situação |
|---|---|---|
| `-1377929346#0` | `1377929346#0.14` | Saul Brandalise → Saul Brandalise |
| `-E4` | `E4` | XV de Novembro → XV de Novembro |
| `-103925179#1` | `103925179#1` | Rua Brasil → Rua Brasil |

## Pares equivalentes a verificar

| Origem | Destino | Via / referência |
|---|---|---|
| `-102361495#0` | `102361495#0` | Antônio Marafon |
| `-102361574.302` | `102361574` | Osvaldo Cruz |
| `99643286#2` | `-99643286#2` | XV de Novembro |
| `-E5` | `E5` | Farroupilha |
| `-E6` | `E6` | Nicolau Cavon |

Esses pares ainda devem ser avaliados individualmente antes de serem bloqueados.

---

# Observações dos testes preliminares

## Saul Brandalise

A análise OD do fluxo 650 indicou quantidade relevante de veículos entrando
pela Saul Brandalise e utilizando destinos como:

- `1377929346#0.14`;
- `E4`;
- `-99643286#2`;
- `103925179#1`;
- `99429213#1`.

O par Saul Brandalise → Saul Brandalise gerou viagens circulares pelo centro e
deve ser tratado separadamente da simples classificação dos pesos.

## Edge `99429213#1`

Durante a inspeção visual, foi observada uma quantidade aparentemente elevada
de veículos seguindo para essa saída, inclusive veículos provenientes da Saul
Brandalise.

A classificação dessa saída deve ser revista antes da definição final dos
pesos.

## Edge `103925179#1`

Também foi observado fluxo aparentemente elevado em direção a essa saída,
inclusive viagens provenientes da Saul Brandalise.

A classificação dessa saída deve ser revista juntamente com `99429213#1`.

## Edge `157964297` — Pedro Andreazza

Foi observada uma diferença entre o comportamento local dos motoristas e o
comportamento de mudança de faixa produzido pelo SUMO.

Na situação real, os motoristas frequentemente utilizam a faixa da direita ao
longo da Pedro Andreazza e podem realizar mudanças de faixa buscando maior
velocidade. A mudança para a faixa esquerda em função da rota costuma ocorrer
mais adiante, principalmente no trecho seguinte, próximo ao shopping.

No SUMO, alguns veículos realizam a mudança estratégica de faixa com muita
antecedência porque a rota futura já é conhecida pelo modelo.

Por enquanto, esse comportamento será tratado como uma limitação da
representação microscópica do cenário, sem alterar artificialmente a
configuração da edge apenas para reproduzir essa preferência local.

---

# Situação atual

A classificação deste documento ainda pertence à etapa de testes preliminares.

Antes da próxima bateria de experimentos, devem ser definidos:

1. classificação final das origens nas cinco categorias;
2. classificação final dos destinos nas cinco categorias;
3. pares origem-destino que serão bloqueados;
4. novos pesos utilizados pelo gerador;
5. validação da distribuição resultante antes de alterar o fluxo total.

O fluxo 650 será mantido inicialmente durante essa avaliação para permitir
verificar se a redistribuição da demanda reduz as concentrações artificiais
observadas sem simplesmente diminuir o número total de veículos.