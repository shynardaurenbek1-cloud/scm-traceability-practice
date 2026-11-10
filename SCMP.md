# Конфигурацияны басқару жоспары (оқу жобасы)

- Қолданылуы: scm-traceability Python коды, тесттер, workflow, құжаттама.
- Рөлдер: әзірлеуші (іске асыру), тексеруші (мақұлдау), релиз менеджері (тег).
- CI бірліктері: app.py, tests/test_app.py, pyproject.toml, .github/workflows/ci.yml.
- Өзгеріс: CR тіркеледі → талдау → мақұлдау → feature branch → тест → merge.
- Baseline: тек тексеруден өткен Git commit + v1.0.0 тегі; өзгеріс жаңа commit арқылы.
- Күй есебі: CHANGELOG.md және Git log. Аудит: pytest және ruff.
- Шектеу: оқу үлгісі, ISO/IEC/IEEE 828 сертификаттауы емес.
