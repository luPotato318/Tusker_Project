# Histórico de versões do PIEM Tusker Power

Esta pasta é o registro oficial e separado das versões disponibilizadas no projeto. O arquivo executável de versão continua em `piem/version.py`; os documentos daqui preservam o escopo, as mudanças e as orientações de atualização.

| Versão | Data | Nome | Documento |
| --- | --- | --- | --- |
| 3.1.0 | 31/08/2026 | Operational Command | [3.1.0.md](3.1.0.md) |
| 3.0.0 | 31/08/2026 | Enterprise Horizon | [3.0.0.md](3.0.0.md) |
| 2.2.0 | 27/08/2026 | Apex Evolution Release | [2.2.0.md](2.2.0.md) |
| 2.1.2 | 15/07/2026 | Tusker Power Initial Release | [2.1.2.md](2.1.2.md) |

## Política de atualização

- Versões `x.y.z` seguem o formato maior, menor e correção.
- Toda nova versão deve atualizar `piem/version.py`, o `README.md` principal e esta pasta.
- Mudanças de banco devem possuir migração Django e, quando aplicável, complemento em `scripts/supabase_schema.sql`.
- Nunca substitua uma nota anterior: crie um novo documento para manter a rastreabilidade.
