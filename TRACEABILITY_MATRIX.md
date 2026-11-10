# Процесс → SCMP ережесі → функция → тест → дәлел

| Процесс | Ереже | Python функция | pytest | Дәлел | Мәртебе |
|---|---|---|---|---|---|
| Identification | §1 | register | test_register | items SQLite | Іске асырылған |
| Change control | §2 | decide/apply | test_unapproved | requests SQLite | Іске асырылған |
| Status accounting | §3 | report | test_report | JSON | Іске асырылған |
| Audit | §4 | audit | test_audit_detect | хэш айырмасы | Ішінара |
| Release | §5 | baseline/link | test_link | baseline ID | Ішінара |

Шектеу: Git commit hash енгізіледі, бірақ GitHub API арқылы расталмайды. ISO/IEC/IEEE 828 сәйкестігін сертификаттамайды.
