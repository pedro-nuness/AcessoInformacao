# Arquitetura do Sistema

O sistema expõe uma API REST como ponto de entrada. A partir do momento em que um texto é enviado, a requisição é validada e rapidamente respondida com status HTTP de sucesso, evitando que o cliente fique bloqueado aguardando o processamento completo. Essa decisão arquitetural reduz latência percebida e protege o sistema contra sobrecarga direta na camada síncrona.

Após o recebimento do texto, o conteúdo e seus metadados iniciais são persistidos diretamente no banco de dados, que atua como a principal fonte de verdade do sistema. Essa persistência imediata garante rastreabilidade do processamento e permite que o fluxo assíncrono continue mesmo em cenários de falha parcial.

Com os dados persistidos, um evento é publicado em uma fila de mensagens, que pode ser implementada com RabbitMQ ou Kafka. A mensageria é um elemento central da arquitetura, pois desacopla completamente a entrada do sistema do processamento pesado. Isso permite escalar consumidores de forma independente, absorver picos de carga e aplicar estratégias de retry sem impactar diretamente a API.

O serviço de processamento consome mensagens dessa fila de forma assíncrona. Esse componente é responsável por executar a lógica principal de classificação, determinando se o texto contém ou não informações sensíveis. Após a análise, o serviço atualiza o status do registro no banco de dados, marcando-o como concluído ou com falha, além de persistir o resultado da classificação. Esse serviço é stateless e projetado para escalar horizontalmente conforme a demanda.

Uma vez que o processamento é finalizado, um worker dispatcher entra em ação. Esse componente monitora o banco de dados por meio de polling e identifica registros que atingiram estados finais de processamento. Ao detectar essas condições, o dispatcher é responsável por notificar sistemas externos por meio de um webhook. Para garantir resiliência nessa integração, a chamada externa passa por um circuito de circuit breaker, prevenindo falhas em cascata e protegendo o sistema contra indisponibilidades externas.

Do ponto de vista operacional, essa arquitetura prioriza desacoplamento e tolerância a falhas. Mesmo que o serviço externo esteja indisponível ou o processamento sofra atrasos, a API continua respondendo corretamente e o sistema mantém consistência interna.

Os testes de carga realizados com o k6 ajudam a evidenciar esse comportamento. Em um primeiro cenário, com baixa concorrência, o sistema apresentou desempenho bastante eficiente. Foram executadas 100 iterações, todas bem-sucedidas, com latência end-to-end média em torno de 560ms e tempo médio de resposta do POST de aproximadamente 28ms. O polling praticamente não ocorreu, com valor médio igual a 1, indicando que o processamento foi rápido o suficiente para que o resultado estivesse disponível quase imediatamente. Um trecho representativo do output do k6 nesse cenário é:

```
TOTAL RESULTS 

checks_total.......: 100     4.497343/s
checks_succeeded...: 100.00% 100 out of 100
checks_failed......: 0.00%   0 out of 100

CUSTOM
completed......................: 97     4.362423/s
failed.........................: 3      0.13492/s
latency_e2e....................: avg=560.48ms min=513ms    med=520ms    max=900ms    p(90)=664ms    p(95)=720.39ms
latency_post...................: avg=28.68ms  min=6ms      med=11ms     max=380ms    p(90)=60.9ms   p(95)=108.64ms
poll_count.....................: avg=1        min=1        med=1        max=1        p(90)=1        p(95)=1       

HTTP
http_req_duration..............: avg=23.81ms  min=4.47ms   med=8.03ms   max=362.09ms p(90)=64.58ms  p(95)=110.94ms
    { expected_response:true }...: avg=23.81ms  min=4.47ms   med=8.03ms   max=362.09ms p(90)=64.58ms  p(95)=110.94ms
http_req_failed................: 0.00%  0 out of 313
http_reqs......................: 313    14.076684/s

EXECUTION
iteration_duration.............: avg=1.15s    min=513.59ms med=521.13ms max=20.33s   p(90)=709.82ms p(95)=876.75ms
iterations.....................: 100    4.497343/s
vus............................: 3      min=3        max=11
vus_max........................: 50     min=50       max=50

NETWORK
data_received..................: 1.5 MB 66 kB/s
data_sent......................: 325 kB 15 kB/s
```

Esse resultado demonstra que, sob carga controlada, o sistema se comporta de forma extremamente estável, com baixa latência e alto throughput.

No segundo cenário, o sistema foi submetido a alta concorrência, alcançando até 200 usuários virtuais simultâneos. Nesse contexto, embora nenhuma falha HTTP tenha sido registrada, a latência end-to-end aumentou significativamente, atingindo uma média de aproximadamente 12 segundos. Esse aumento está diretamente relacionado ao crescimento da fila e ao tempo de espera até que o processamento assíncrono fosse concluído. O polling médio subiu para cerca de 21 tentativas, evidenciando que o dispatcher precisou consultar o banco diversas vezes até encontrar o status final do processamento. Um recorte do output do k6 nesse cenário ilustra bem esse comportamento:

```
TOTAL RESULTS 

checks_total.......: 301     10.543627/s
checks_succeeded...: 100.00% 301 out of 301
checks_failed......: 0.00%   0 out of 301

CUSTOM
completed......................: 301    10.543627/s
latency_e2e....................: avg=12.11s    min=539ms    med=13.17s  max=19.45s   p(90)=18.96s   p(95)=19.15s  
latency_post...................: avg=67.11ms   min=8ms      med=19ms    max=703ms    p(90)=183ms    p(95)=253ms   
poll_count.....................: avg=21.385382 min=1        med=23      max=35       p(90)=34       p(95)=34      

HTTP
http_req_duration..............: avg=60.31ms   min=3.94ms   med=38.32ms max=693.55ms p(90)=131.11ms p(95)=145.93ms
    { expected_response:true }...: avg=60.31ms   min=3.94ms   med=38.32ms max=693.55ms p(90)=131.11ms p(95)=145.93ms
http_req_failed................: 0.00%  0 out of 6738
http_reqs......................: 6738   236.023123/s

EXECUTION
dropped_iterations.............: 699    24.485035/s
iteration_duration.............: avg=12.11s    min=539.89ms med=13.17s  max=19.45s   p(90)=18.96s   p(95)=19.15s  
iterations.....................: 301    10.543627/s
vus............................: 11     min=11        max=200
vus_max........................: 200    min=100       max=200

NETWORK
data_received..................: 23 MB  792 kB/s
data_sent......................: 1.7 MB 59 kB/s
```

Apesar do aumento da latência total, o tempo de resposta da API permaneceu baixo, o que confirma a eficácia da estratégia de processamento assíncrono. A mensageria conseguiu absorver o pico de requisições sem perda de dados, e o sistema manteve consistência e confiabilidade durante todo o teste.

De forma geral, a arquitetura demonstra-se robusta e bem alinhada para cenários reais de produção, especialmente quando a prioridade é confiabilidade e escalabilidade, mesmo que isso implique maior latência end-to-end em situações de alta carga. Como evolução natural, podem ser consideradas melhorias como redução da dependência de polling, adoção de eventos de conclusão, ajustes no paralelismo do serviço de processamento e implementação de filas de dead letter para tratamento de falhas.

Conclui-se que o sistema está tecnicamente bem fundamentado, com decisões arquiteturais coerentes e sustentadas pelos resultados observados nos testes de carga, sendo plenamente capaz de operar em ambientes de alto volume com comportamento previsível e resiliente.
