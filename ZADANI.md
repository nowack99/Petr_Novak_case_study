# Technické zadání — Senior Python Developer

**Odhadovaný čas:** 60–90 minut
**Jazyk:** Python 3.12
**Stack:** FastAPI, SQLAlchemy 2 (async), PostgreSQL, Pydantic v2

---

## Co budujeme

Rozšiřuješ existující API pro správu úkolů v týmu. Systém umožňuje:

- Vytvářet uživatele a přiřazovat jim úkoly
- Sledovat stav úkolů v průběhu jejich životního cyklu (`TODO → IN_PROGRESS → DONE`)
- Řídit přístup — úkol může upravovat pouze jeho vlastník

Část aplikace je již hotová (správa uživatelů). Tvým úkolem je dodat celou část pro správu úkolů — od doménové logiky až po HTTP endpointy a testy.

**Před začátkem prostuduj hotové implementace jako vzor:**

- `app/domain/user.py` — jak vypadá doménový objekt
- `app/db/repositories/user_repository.py` — jak funguje repository a mapping
- `app/services/user_service.py` — jak vypadá servisní vrstva
- `app/api/v1/users.py` — jak jsou strukturovány route handlery

Spuštění:

```bash
cp .env.example .env
make build
make migrate
```

---

## Architektura projektu

```text
app/api/v1/           HTTP vrstva — pouze routing, validace vstupu/výstupu
app/services/         Business logika a orchestrace
app/db/repositories/  Přístup k databázi, mapování ORM ↔ doména
app/db/models/        SQLAlchemy ORM modely
app/domain/           Čisté Python objekty — žádné frameworkové závislosti
app/schemas/          Pydantic modely — pouze na HTTP hranici
```

**Pravidlo závislostí:** závislosti tečou pouze dolů.
Servisní vrstva nesmí importovat z FastAPI. Doménová vrstva nesmí importovat nic z ostatních vrstev.

---

## Část 1 — Doménová logika

Vytvoř soubor `app/domain/task.py`.

### TaskStatus

Vytvoř `StrEnum` s hodnotami: `TODO`, `IN_PROGRESS`, `DONE`.

### Task

Vytvoř `frozen` dataclass s těmito atributy:

| Atribut | Typ | Poznámka |
| --- | --- | --- |
| `id` | `UUID` | |
| `title` | `str` | |
| `status` | `TaskStatus` | |
| `owner_id` | `UUID` | |
| `created_at` | `datetime` | |
| `updated_at` | `datetime` | |
| `description` | `str \| None` | výchozí `None` |
| `assignee_id` | `UUID \| None` | výchozí `None` |

Implementuj tyto metody:

**`can_be_edited_by(user: User) -> bool`**

- Vrať `True` pouze pokud je `user.id == self.owner_id`
- Neaktivní uživatel (`is_active = False`) nesmí upravovat nic

**`complete() -> Task`**

- Přechod je povolen pouze ze stavu `IN_PROGRESS`
- Pro neplatný přechod vyvolej `ValueError` s popisnou zprávou
- Vrať **novou instanci** — `Task` je `frozen`, nesmíš mutovat `self`

**`assign_to(user: User) -> Task`**

- Přiřazení je povoleno pouze aktivnímu uživateli
- Úkol ve stavu `DONE` nelze přeřadit
- Vrať **novou instanci**

---

## Část 2 — Repository vrstva

Vytvoř soubor `app/db/repositories/task_repository.py`.

Implementuj třídu `TaskRepository` rozšiřující `BaseRepository[TaskModel, Task]` (viz `app/db/repositories/base.py`).

Povinné metody:

| Metoda | Popis |
| --- | --- |
| `_to_domain(model: TaskModel) -> Task` | Převod ORM modelu na doménový objekt |
| `_to_model(domain: Task) -> TaskModel` | Převod doménového objektu na ORM model |
| `get_by_owner(owner_id: UUID) -> list[Task]` | Všechny úkoly daného vlastníka |
| `get_by_assignee(assignee_id: UUID) -> list[Task]` | Všechny úkoly přiřazené danému uživateli |
| `get_by_status(status: TaskStatus) -> list[Task]` | Všechny úkoly s daným stavem |

Nezapomeň zaregistrovat `get_task_repository` dependency v `app/dependencies.py`.

---

## Část 3 — Servisní vrstva

Vytvoř soubor `app/services/task_service.py`.

Implementuj třídu `TaskService` přijímající `TaskRepository` a `UserRepository` v konstruktoru.

Povinné metody:

| Metoda | Popis |
| --- | --- |
| `create_task(data: TaskCreate, owner_id: UUID) -> Task` | Vytvoří nový úkol |
| `get_task(task_id: UUID) -> Task` | Vrátí úkol nebo vyhodí 404 |
| `list_tasks(owner_id, status) -> list[Task]` | Filtrovaný seznam úkolů |
| `update_task(task_id, data: TaskUpdate, requesting_user_id) -> Task` | Upraví pole úkolu |
| `assign_task(task_id, assignee_id, requesting_user_id) -> Task` | Přiřadí úkol uživateli |
| `complete_task(task_id, requesting_user_id) -> Task` | Označí úkol jako DONE |

Požadavky:

- V metodách `assign_task` a `complete_task` **musíš volat metody doménového objektu** (`task.assign_to()`, `task.complete()`) — nesmíš obcházet doménovou logiku přímou manipulací s daty
- Správné HTTP chybové kódy: `404` (nenalezeno), `403` (nedostatečná oprávnění), `422` (neplatný přechod stavu)

---

## Část 4 — API vrstva

Vytvoř soubor `app/api/v1/tasks.py` a zaregistruj router v `app/api/v1/router.py`.

Povinné endpointy:

| Metoda | Cesta | Popis |
| --- | --- | --- |
| `POST` | `/api/v1/tasks` | Vytvoří úkol, vrátí `201` |
| `GET` | `/api/v1/tasks` | Seznam úkolů, filtrování přes query params `owner_id`, `status` |
| `GET` | `/api/v1/tasks/{task_id}` | Detail úkolu |
| `PATCH` | `/api/v1/tasks/{task_id}` | Úprava polí úkolu |
| `POST` | `/api/v1/tasks/{task_id}/assign` | Přiřazení úkolu uživateli |
| `POST` | `/api/v1/tasks/{task_id}/complete` | Označení úkolu jako DONE |

Pydantic schémata pro request/response si vytvoř sám v `app/schemas/task.py`.

---

## Část 5 — Testy

Napiš testy pro svou implementaci.

**Unit testy** (`tests/test_domain.py`) — bez databáze, pouze čistá Python logika:

- `Task.can_be_edited_by` — vlastník, cizí uživatel, neaktivní uživatel
- `Task.complete` — platný přechod, neplatný přechod, vrací novou instanci
- `Task.assign_to` — aktivní uživatel, neaktivní uživatel, DONE úkol, vrací novou instanci

**Integrační testy** (`tests/test_tasks.py`) — přes HTTP klienta:

- Vytvoření úkolu
- Získání úkolu (existující, neexistující)
- Filtrování seznamu podle vlastníka
- Přiřazení úkolu
- Dokončení úkolu
- Pokus o úpravu cizího úkolu (očekávaný 403)

Spuštění:

```bash
make test
```

---

## Část 6 — Rozšíření (senior úroveň)

> Řeš až po dokončení částí 1–5.

### 6.1 Vlastní výjimky

Servisní vrstva nesmí přímo vyhazovat `HTTPException` — to je závislost na HTTP vrstvě.

Navrhni a implementuj vlastní výjimky (např. `TaskNotFoundError`, `PermissionDeniedError`, `InvalidTransitionError`) a zachyť je na úrovni FastAPI pomocí exception handleru.

### 6.2 Stránkování

Přidej stránkování na `GET /api/v1/tasks`:

- Query parametry: `limit: int = 20`, `offset: int = 0`
- Response obal s metadaty: `items`, `total`, `limit`, `offset`
- Vytvoř generický Pydantic model `Page[T]`

### 6.3 Historie úkolů

Navrhni a implementuj `GET /api/v1/tasks/{task_id}/history` — seznam změn stavu úkolu (kdo, kdy, z jakého stavu, do jakého).

Musíš navrhnout od nuly: doménový objekt, ORM model, migraci, repository, service metodu a automatické zaznamenávání při každé změně stavu.

---

## Co hodnotíme

| Oblast | Na co se díváme |
| --- | --- |
| **Doménová logika** | Immutabilita, správné výjimky, žádné frameworkové závislosti |
| **Architektura** | Dodržení hranic vrstev, tok závislostí dolů |
| **Repository pattern** | Čistý mapping, žádná business logika v DB vrstvě |
| **Servisní vrstva** | Volání doménových metod, ne přímá manipulace s daty |
| **Testovatelnost** | Unit testy bez DB, izolace závislostí |
| **Chybové stavy** | Správné HTTP kódy, popisné zprávy |
| **Kód** | Čitelnost, konzistence se stylem projektu |

